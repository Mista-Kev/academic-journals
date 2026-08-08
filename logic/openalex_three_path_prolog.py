"""Build temporal pathway evidence for the frozen OpenAlex AI dataset.

The default analysis unit is one focal author/article pair. Histories stay
inside the frozen corpus and evidence must be strictly earlier than the focal
article date.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


RAW_FILENAME = "openalex_ai_raw_v1_0.jsonl"
SEMICLEAN_FILENAME = "openalex_ai_semiclean_v1_0.csv"
RULES_FILENAME = "openalex_three_path_rules.pl"


@dataclass(frozen=True)
class Article:
    work_id: str
    publication_date: str
    journal_id: str
    parent_publisher_id: str | None
    author_ids: tuple[str | None, ...]


@dataclass(frozen=True)
class PublisherMapping:
    journal_id: str
    journal_name: str | None
    immediate_publisher_id: str | None
    immediate_publisher_name: str | None
    parent_publisher_id: str | None
    parent_publisher_name: str | None
    lineage_ids: tuple[str, ...]
    lineage_names: tuple[str, ...]

    @property
    def is_unresolved(self) -> bool:
        return self.parent_publisher_id is None


@dataclass(frozen=True)
class Evidence:
    prior_work_id: str
    prior_author_id: str
    prior_journal_id: str
    prior_parent_publisher_id: str | None
    prior_date: str

    def to_dict(self) -> dict[str, str | None]:
        return {
            "prior_work_id": self.prior_work_id,
            "prior_author_id": self.prior_author_id,
            "prior_journal_id": self.prior_journal_id,
            "prior_parent_publisher_id": self.prior_parent_publisher_id,
            "prior_date": self.prior_date,
        }


@dataclass(frozen=True)
class PathwayResult:
    focal_work_id: str
    focal_author_id: str
    focal_journal_id: str
    focal_parent_publisher_id: str | None
    focal_date: str
    journal_evidence: tuple[Evidence, ...]
    publisher_evidence: tuple[Evidence, ...]
    coauthor_evidence: tuple[Evidence, ...]

    @property
    def journal_path(self) -> bool:
        return bool(self.journal_evidence)

    @property
    def publisher_path(self) -> bool:
        return bool(self.publisher_evidence)

    @property
    def coauthor_path(self) -> bool:
        return bool(self.coauthor_evidence)

    def to_csv_row(self, max_evidence: int | None = 3) -> dict[str, str | int | bool | None]:
        return {
            "focal_work_id": self.focal_work_id,
            "focal_author_id": self.focal_author_id,
            "focal_journal_id": self.focal_journal_id,
            "focal_parent_publisher_id": self.focal_parent_publisher_id,
            "focal_date": self.focal_date,
            "journal_path": self.journal_path,
            "publisher_path": self.publisher_path,
            "coauthor_path": self.coauthor_path,
            "journal_evidence_count": len(self.journal_evidence),
            "publisher_evidence_count": len(self.publisher_evidence),
            "coauthor_evidence_count": len(self.coauthor_evidence),
            "journal_evidence_json": evidence_json(self.journal_evidence, max_evidence),
            "publisher_evidence_json": evidence_json(self.publisher_evidence, max_evidence),
            "coauthor_evidence_json": evidence_json(self.coauthor_evidence, max_evidence),
        }


def short_id(value: object) -> str | None:
    if value is None or value == "":
        return None
    return str(value).rstrip("/").split("/")[-1]


def normalized_parent_publisher_id(lineage: Sequence[object] | None) -> str | None:
    if not lineage:
        return None
    ids = [short_id(item) for item in lineage]
    ids = [item for item in ids if item]
    return ids[-1] if ids else None


def normalized_parent_publisher_name(lineage_names: Sequence[object] | None) -> str | None:
    if not lineage_names:
        return None
    names = [str(item) for item in lineage_names if item]
    return names[-1] if names else None


def load_journal_parent_publishers(raw_jsonl_path: Path) -> dict[str, PublisherMapping]:
    mappings: dict[str, PublisherMapping] = {}

    with raw_jsonl_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                work = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON on raw line {line_number}.") from error

            source = ((work.get("primary_location") or {}).get("source") or {})
            journal_id = short_id(source.get("id"))
            if not journal_id:
                continue

            candidate = _publisher_mapping_from_source(source, journal_id)
            existing = mappings.get(journal_id)
            if existing is None:
                mappings[journal_id] = candidate
            elif existing.is_unresolved and not candidate.is_unresolved:
                mappings[journal_id] = candidate
            elif (
                not candidate.is_unresolved
                and not existing.is_unresolved
                and candidate.lineage_ids != existing.lineage_ids
            ):
                raise ValueError(
                    "Conflicting publisher lineages for "
                    f"{journal_id}: {existing.lineage_ids} != {candidate.lineage_ids}"
                )

    return mappings


def load_articles_from_semiclean_csv(
    semiclean_csv_path: Path,
    publisher_mappings: dict[str, PublisherMapping],
) -> list[Article]:
    articles: list[Article] = []

    with semiclean_csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_number, row in enumerate(reader, start=2):
            work_id = row.get("work_id") or ""
            publication_date = row.get("publication_date") or ""
            journal_id = row.get("journal_id") or ""
            if not work_id or not publication_date or not journal_id:
                continue

            authors = _author_ids_from_json(row.get("authorships_json") or "[]", row_number)
            mapping = publisher_mappings.get(journal_id)
            parent_publisher_id = mapping.parent_publisher_id if mapping else None
            articles.append(
                Article(
                    work_id=work_id,
                    publication_date=publication_date,
                    journal_id=journal_id,
                    parent_publisher_id=parent_publisher_id,
                    author_ids=tuple(authors),
                )
            )

    return articles


def evaluate_pathways(
    articles: Iterable[Article],
    focal_start_year: int | None = None,
    focal_end_year: int | None = None,
) -> list[PathwayResult]:
    article_list = list(articles)
    by_author_journal: dict[tuple[str, str], list[Article]] = defaultdict(list)
    by_author_publisher: dict[tuple[str, str], list[Article]] = defaultdict(list)

    for article in article_list:
        for author_id in unique_present(article.author_ids):
            by_author_journal[(author_id, article.journal_id)].append(article)
            if article.parent_publisher_id:
                by_author_publisher[(author_id, article.parent_publisher_id)].append(article)

    for grouped_articles in by_author_journal.values():
        grouped_articles.sort(key=article_sort_key)
    for grouped_articles in by_author_publisher.values():
        grouped_articles.sort(key=article_sort_key)

    results: list[PathwayResult] = []
    for focal in sorted(article_list, key=article_sort_key):
        if not is_focal_year(focal.publication_date, focal_start_year, focal_end_year):
            continue
        focal_authors = unique_present(focal.author_ids)
        for focal_author_id in focal_authors:
            journal_evidence = tuple(
                evidence_for_prior(prior, focal_author_id)
                for prior in by_author_journal.get((focal_author_id, focal.journal_id), [])
                if is_strictly_prior(prior, focal)
            )
            publisher_evidence = tuple(
                evidence_for_prior(prior, focal_author_id)
                for prior in by_author_publisher.get(
                    (focal_author_id, focal.parent_publisher_id or ""), []
                )
                if focal.parent_publisher_id
                and prior.journal_id != focal.journal_id
                and is_strictly_prior(prior, focal)
            )
            coauthor_evidence = tuple(
                evidence_for_prior(prior, coauthor_id)
                for coauthor_id in focal_authors
                if coauthor_id != focal_author_id
                for prior in by_author_journal.get((coauthor_id, focal.journal_id), [])
                if is_strictly_prior(prior, focal)
            )

            results.append(
                PathwayResult(
                    focal_work_id=focal.work_id,
                    focal_author_id=focal_author_id,
                    focal_journal_id=focal.journal_id,
                    focal_parent_publisher_id=focal.parent_publisher_id,
                    focal_date=focal.publication_date,
                    journal_evidence=sort_evidence(journal_evidence),
                    publisher_evidence=sort_evidence(publisher_evidence),
                    coauthor_evidence=sort_evidence(coauthor_evidence),
                )
            )

    return results


def find_swipl_executable() -> Path:
    candidates: list[Path] = []
    configured_path = os.environ.get("SWIPL_PATH")
    if configured_path:
        candidates.append(Path(configured_path).expanduser())

    path_from_environment = shutil.which("swipl")
    if path_from_environment:
        candidates.append(Path(path_from_environment))

    candidates.append(Path(r"C:\Program Files\swipl\bin\swipl.exe"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(
        "SWI-Prolog wurde nicht gefunden. Installiere SWI-Prolog oder setze SWIPL_PATH."
    )


def run_prolog_analysis(
    facts_path: Path,
    rules_path: Path,
    articles: Sequence[Article],
) -> list[PathwayResult]:
    executable = find_swipl_executable()
    completed = subprocess.run(
        [
            str(executable),
            "-q",
            "-s",
            str(facts_path),
            "-s",
            str(rules_path),
            "-g",
            "emit_pathway_results,halt",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f"SWI-Prolog-Analyse fehlgeschlagen: {detail}")

    return pathway_results_from_prolog_output(completed.stdout, articles)


def pathway_results_from_prolog_output(
    output: str,
    articles: Sequence[Article],
) -> list[PathwayResult]:
    flags: dict[tuple[str, str], tuple[bool, bool, bool]] = {}
    evidence_by_path: dict[
        tuple[str, str], dict[str, list[Evidence]]
    ] = defaultdict(lambda: defaultdict(list))

    for line_number, line in enumerate(output.splitlines(), start=1):
        if not line.strip():
            continue
        fields = line.split("|")
        record_type = fields[0]
        if record_type == "FLAG":
            if len(fields) != 6:
                raise ValueError(f"Ungültiger FLAG-Datensatz aus Prolog in Zeile {line_number}.")
            key = (fields[1], fields[2])
            if key in flags:
                raise ValueError(f"Doppelter FLAG-Datensatz aus Prolog in Zeile {line_number}.")
            flags[key] = tuple(parse_prolog_bool(value) for value in fields[3:6])
        elif record_type == "EVIDENCE":
            if len(fields) != 9:
                raise ValueError(
                    f"Ungültiger EVIDENCE-Datensatz aus Prolog in Zeile {line_number}."
                )
            path_type = fields[3]
            if path_type not in {"journal", "publisher", "coauthor"}:
                raise ValueError(f"Unbekannter Pfadtyp aus Prolog in Zeile {line_number}.")
            key = (fields[1], fields[2])
            evidence_by_path[key][path_type].append(
                Evidence(
                    prior_work_id=fields[4],
                    prior_author_id=fields[5],
                    prior_journal_id=fields[6],
                    prior_parent_publisher_id=prolog_none(fields[7]),
                    prior_date=fields[8],
                )
            )
        else:
            raise ValueError(f"Unbekannter Prolog-Datensatz in Zeile {line_number}.")

    if not flags:
        raise ValueError("Prolog hat keine focal_pair-Ergebnisse zurückgegeben.")

    article_by_work = {article.work_id: article for article in articles}
    results: list[PathwayResult] = []
    ordered_keys = sorted(
        flags,
        key=lambda key: (*article_sort_key(article_by_work[key[0]]), key[1]),
    )
    for focal_work_id, focal_author_id in ordered_keys:
        focal = article_by_work.get(focal_work_id)
        if focal is None:
            raise ValueError(f"Prolog verwies auf unbekanntes Werk: {focal_work_id}")
        path_evidence = evidence_by_path.get((focal_work_id, focal_author_id), {})
        journal_evidence = sort_evidence(path_evidence.get("journal", []))
        publisher_evidence = sort_evidence(path_evidence.get("publisher", []))
        coauthor_evidence = sort_evidence(path_evidence.get("coauthor", []))
        expected_flags = (
            bool(journal_evidence),
            bool(publisher_evidence),
            bool(coauthor_evidence),
        )
        if expected_flags != flags[(focal_work_id, focal_author_id)]:
            raise ValueError(
                "Prolog-Flags stimmen nicht mit den ausgegebenen Belegen überein: "
                f"{focal_work_id}/{focal_author_id}"
            )
        results.append(
            PathwayResult(
                focal_work_id=focal_work_id,
                focal_author_id=focal_author_id,
                focal_journal_id=focal.journal_id,
                focal_parent_publisher_id=focal.parent_publisher_id,
                focal_date=focal.publication_date,
                journal_evidence=journal_evidence,
                publisher_evidence=publisher_evidence,
                coauthor_evidence=coauthor_evidence,
            )
        )
    return results


def parse_prolog_bool(value: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError(f"Ungültiger Boolean-Wert aus Prolog: {value}")


def prolog_none(value: str) -> str | None:
    return None if value == "none" else value


def render_prolog_facts(
    articles: Iterable[Article],
    focal_start_year: int | None = None,
    focal_end_year: int | None = None,
) -> str:
    article_list = sorted(list(articles), key=article_sort_key)
    lines = [
        "% Generated facts for openalex_three_path_rules.pl.",
        "% Dates are ISO strings; SWI-Prolog term order is used for strict temporal checks.",
        ":- discontiguous journal_parent_publisher/2.",
        ":- discontiguous work/4.",
        ":- discontiguous authorship/2.",
        ":- discontiguous focal_pair/2.",
    ]
    seen_journal_publishers: set[tuple[str, str | None]] = set()

    for article in article_list:
        publisher_key = (article.journal_id, article.parent_publisher_id)
        if publisher_key not in seen_journal_publishers:
            lines.append(
                "journal_parent_publisher("
                f"{prolog_atom(article.journal_id)},"
                f"{prolog_atom(article.parent_publisher_id)})."
            )
            seen_journal_publishers.add(publisher_key)

        lines.append(
            "work("
            f"{prolog_atom(article.work_id)},"
            f"{prolog_atom(article.publication_date)},"
            f"{prolog_atom(article.journal_id)},"
            f"{prolog_atom(article.parent_publisher_id)})."
        )
        for author_id in unique_present(article.author_ids):
            lines.append(f"authorship({prolog_atom(article.work_id)},{prolog_atom(author_id)}).")
            if is_focal_year(article.publication_date, focal_start_year, focal_end_year):
                lines.append(f"focal_pair({prolog_atom(article.work_id)},{prolog_atom(author_id)}).")

    return "\n".join(lines) + "\n"


def write_pathway_results_csv(
    results: Iterable[PathwayResult],
    output_path: Path,
    max_evidence: int | None = 3,
) -> None:
    fieldnames = [
        "focal_work_id",
        "focal_author_id",
        "focal_journal_id",
        "focal_parent_publisher_id",
        "focal_date",
        "journal_path",
        "publisher_path",
        "coauthor_path",
        "journal_evidence_count",
        "publisher_evidence_count",
        "coauthor_evidence_count",
        "journal_evidence_json",
        "publisher_evidence_json",
        "coauthor_evidence_json",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result.to_csv_row(max_evidence=max_evidence))


def write_pathway_flags_csv(
    results: Iterable[PathwayResult],
    output_path: Path,
) -> None:
    fieldnames = [
        "focal_work_id",
        "focal_author_id",
        "focal_journal_id",
        "focal_parent_publisher_id",
        "focal_date",
        "journal_path",
        "publisher_path",
        "coauthor_path",
        "journal_evidence_count",
        "publisher_evidence_count",
        "coauthor_evidence_count",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "focal_work_id": result.focal_work_id,
                    "focal_author_id": result.focal_author_id,
                    "focal_journal_id": result.focal_journal_id,
                    "focal_parent_publisher_id": result.focal_parent_publisher_id,
                    "focal_date": result.focal_date,
                    "journal_path": result.journal_path,
                    "publisher_path": result.publisher_path,
                    "coauthor_path": result.coauthor_path,
                    "journal_evidence_count": len(result.journal_evidence),
                    "publisher_evidence_count": len(result.publisher_evidence),
                    "coauthor_evidence_count": len(result.coauthor_evidence),
                }
            )


def write_pathway_evidence_csv(
    results: Iterable[PathwayResult],
    output_path: Path,
) -> None:
    fieldnames = [
        "focal_work_id",
        "focal_author_id",
        "path_type",
        "prior_work_id",
        "prior_author_id",
        "prior_journal_id",
        "prior_parent_publisher_id",
        "prior_date",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            for path_type, evidence_rows in (
                ("journal", result.journal_evidence),
                ("publisher", result.publisher_evidence),
                ("coauthor", result.coauthor_evidence),
            ):
                for evidence in evidence_rows:
                    writer.writerow(
                        {
                            "focal_work_id": result.focal_work_id,
                            "focal_author_id": result.focal_author_id,
                            "path_type": path_type,
                            **evidence.to_dict(),
                        }
                    )


def write_journal_parent_publishers_csv(
    mappings: dict[str, PublisherMapping],
    output_path: Path,
) -> None:
    fieldnames = [
        "journal_id",
        "journal_name",
        "immediate_publisher_id",
        "immediate_publisher_name",
        "parent_publisher_id",
        "parent_publisher_name",
        "lineage_ids_json",
        "lineage_names_json",
        "is_unresolved",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for mapping in sorted(mappings.values(), key=lambda item: item.journal_id):
            writer.writerow(
                {
                    "journal_id": mapping.journal_id,
                    "journal_name": mapping.journal_name,
                    "immediate_publisher_id": mapping.immediate_publisher_id,
                    "immediate_publisher_name": mapping.immediate_publisher_name,
                    "parent_publisher_id": mapping.parent_publisher_id,
                    "parent_publisher_name": mapping.parent_publisher_name,
                    "lineage_ids_json": json.dumps(mapping.lineage_ids, ensure_ascii=False),
                    "lineage_names_json": json.dumps(mapping.lineage_names, ensure_ascii=False),
                    "is_unresolved": mapping.is_unresolved,
                }
            )


def write_prolog_facts(
    articles: Iterable[Article],
    output_path: Path,
    focal_start_year: int | None = None,
    focal_end_year: int | None = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_prolog_facts(
            articles,
            focal_start_year=focal_start_year,
            focal_end_year=focal_end_year,
        ),
        encoding="utf-8",
    )


def evidence_json(evidence: Sequence[Evidence], max_evidence: int | None = 3) -> str:
    selected = evidence
    if max_evidence is not None and max_evidence > 0:
        selected = evidence[:max_evidence]
    return json.dumps([item.to_dict() for item in selected], ensure_ascii=False, separators=(",", ":"))


def sort_evidence(evidence: Iterable[Evidence]) -> tuple[Evidence, ...]:
    return tuple(
        sorted(
            evidence,
            key=lambda item: (
                item.prior_date,
                item.prior_work_id,
                item.prior_author_id,
                item.prior_journal_id,
            ),
        )
    )


def evidence_for_prior(prior: Article, prior_author_id: str) -> Evidence:
    return Evidence(
        prior_work_id=prior.work_id,
        prior_author_id=prior_author_id,
        prior_journal_id=prior.journal_id,
        prior_parent_publisher_id=prior.parent_publisher_id,
        prior_date=prior.publication_date,
    )


def unique_present(values: Iterable[str | None]) -> tuple[str, ...]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if not value:
            continue
        text = str(value)
        if text not in seen:
            seen.add(text)
            unique.append(text)
    return tuple(unique)


def article_sort_key(article: Article) -> tuple[str, str]:
    return article.publication_date, article.work_id


def is_strictly_prior(prior: Article, focal: Article) -> bool:
    return prior.work_id != focal.work_id and prior.publication_date < focal.publication_date


def is_focal_year(
    publication_date: str,
    focal_start_year: int | None,
    focal_end_year: int | None,
) -> bool:
    year = year_from_iso_date(publication_date)
    if year is None:
        return False
    if focal_start_year is not None and year < focal_start_year:
        return False
    if focal_end_year is not None and year > focal_end_year:
        return False
    return True


def year_from_iso_date(publication_date: str) -> int | None:
    if len(publication_date) < 4:
        return None
    try:
        return int(publication_date[:4])
    except ValueError:
        return None


def prolog_atom(value: object) -> str:
    if value is None or value == "":
        return "none"
    text = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{text}'"


def resolve_data_paths(
    data_dir: Path | None = None,
    raw_jsonl: Path | None = None,
    semiclean_csv: Path | None = None,
) -> tuple[Path, Path, Path]:
    resolved_data_dir = data_dir or default_data_dir()
    raw_path = raw_jsonl or resolved_data_dir / RAW_FILENAME
    csv_path = semiclean_csv or resolved_data_dir / SEMICLEAN_FILENAME
    return resolved_data_dir, raw_path, csv_path


def default_data_dir() -> Path:
    env_dir = os.environ.get("OPENALEX_DATA_DIR")
    if env_dir:
        return Path(env_dir)

    cwd = Path.cwd()
    script_dir = Path(__file__).resolve().parent
    candidates: list[Path] = []

    def add_candidate(path: Path) -> None:
        if path not in candidates:
            candidates.append(path)

    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").exists():
            add_candidate(parent / "data")
            break

    for parent in [script_dir, *script_dir.parents]:
        if (parent / ".git").exists():
            add_candidate(parent / "data")
            break

    for base in (cwd, script_dir):
        add_candidate(base / "data")
        add_candidate(base / "openalex_ai_dataset_v1_0")
        add_candidate(base)

    for candidate in candidates:
        if (candidate / RAW_FILENAME).exists() or (candidate / SEMICLEAN_FILENAME).exists():
            return candidate

    return script_dir / "data"


def default_output_dir() -> Path:
    return Path(__file__).resolve().parent / "openalex_three_path_output"


def build_outputs(
    data_dir: Path | None,
    raw_jsonl: Path | None,
    semiclean_csv: Path | None,
    out_dir: Path,
    focal_start_year: int | None,
    focal_end_year: int | None,
    max_evidence: int | None,
) -> dict[str, object]:
    resolved_data_dir, raw_path, csv_path = resolve_data_paths(data_dir, raw_jsonl, semiclean_csv)
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw JSONL not found: {raw_path}")
    if not csv_path.exists():
        raise FileNotFoundError(f"Semi-clean CSV not found: {csv_path}")

    mappings = load_journal_parent_publishers(raw_path)
    articles = load_articles_from_semiclean_csv(csv_path, mappings)

    out_dir.mkdir(parents=True, exist_ok=True)
    mapping_path = out_dir / "journal_parent_publishers.csv"
    results_path = out_dir / "pathway_results.csv"
    flags_path = out_dir / "pathway_flags.csv"
    evidence_path = out_dir / "pathway_evidence.csv"
    facts_path = out_dir / "openalex_three_path_facts.pl"
    rules_path = out_dir / RULES_FILENAME

    write_journal_parent_publishers_csv(mappings, mapping_path)
    write_prolog_facts(
        articles,
        facts_path,
        focal_start_year=focal_start_year,
        focal_end_year=focal_end_year,
    )
    copy_rules_file(rules_path)
    results = run_prolog_analysis(facts_path, rules_path, articles)
    write_pathway_results_csv(results, results_path, max_evidence=max_evidence)
    write_pathway_flags_csv(results, flags_path)
    write_pathway_evidence_csv(results, evidence_path)

    run_metadata = {
        "data_dir": str(resolved_data_dir),
        "raw_jsonl": str(raw_path),
        "semiclean_csv": str(csv_path),
        "analysis_engine": "SWI-Prolog",
        "articles": len(articles),
        "journals_with_publisher_mapping": len(mappings),
        "unresolved_journal_publishers": sum(1 for item in mappings.values() if item.is_unresolved),
        "focal_pairs": len(results),
        "focal_start_year": focal_start_year,
        "focal_end_year": focal_end_year,
        "journal_path_true": sum(1 for item in results if item.journal_path),
        "publisher_path_true": sum(1 for item in results if item.publisher_path),
        "coauthor_path_true": sum(1 for item in results if item.coauthor_path),
        "max_evidence_per_path_in_csv": max_evidence,
        "outputs": {
            "journal_parent_publishers_csv": str(mapping_path),
            "pathway_results_csv": str(results_path),
            "pathway_flags_csv": str(flags_path),
            "pathway_evidence_csv": str(evidence_path),
            "prolog_facts": str(facts_path),
            "prolog_rules": str(rules_path),
        },
    }
    return run_metadata


def copy_rules_file(destination: Path) -> None:
    source = Path(__file__).with_name(RULES_FILENAME)
    if not source.exists():
        raise FileNotFoundError(f"Prolog rules file not found: {source}")
    shutil.copyfile(source, destination)


def _publisher_mapping_from_source(source: dict[str, object], journal_id: str) -> PublisherMapping:
    lineage_ids = tuple(
        item for item in (short_id(value) for value in source.get("host_organization_lineage") or []) if item
    )
    lineage_names = tuple(str(value) for value in source.get("host_organization_lineage_names") or [] if value)
    parent_publisher_id = lineage_ids[-1] if lineage_ids else None
    parent_publisher_name = lineage_names[-1] if lineage_names else None
    immediate_publisher_id = short_id(source.get("host_organization")) or (
        lineage_ids[0] if lineage_ids else None
    )
    immediate_publisher_name = source.get("host_organization_name") or (
        lineage_names[0] if lineage_names else None
    )

    return PublisherMapping(
        journal_id=journal_id,
        journal_name=source.get("display_name"),
        immediate_publisher_id=immediate_publisher_id,
        immediate_publisher_name=str(immediate_publisher_name) if immediate_publisher_name else None,
        parent_publisher_id=parent_publisher_id,
        parent_publisher_name=parent_publisher_name,
        lineage_ids=lineage_ids,
        lineage_names=lineage_names,
    )


def _author_ids_from_json(authorships_json: str, row_number: int) -> tuple[str, ...]:
    try:
        authorships = json.loads(authorships_json)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid authorships_json in CSV row {row_number}.") from error
    if not isinstance(authorships, list):
        raise ValueError(f"authorships_json must be a list in CSV row {row_number}.")

    author_ids: list[str | None] = []
    for authorship in authorships:
        if isinstance(authorship, dict):
            author_ids.append(short_id(authorship.get("author_id")))
    return unique_present(author_ids)


def parse_max_evidence(value: int) -> int | None:
    if value < 0:
        raise argparse.ArgumentTypeError("--max-evidence must be zero or positive.")
    return None if value == 0 else value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build Python and SWI-Prolog temporal pathway evidence for the frozen OpenAlex AI dataset."
    )
    parser.add_argument("--data-dir", type=Path, default=None, help="Directory containing the frozen v1.0 files.")
    parser.add_argument("--raw-jsonl", type=Path, default=None, help=f"Path to {RAW_FILENAME}.")
    parser.add_argument("--semiclean-csv", type=Path, default=None, help=f"Path to {SEMICLEAN_FILENAME}.")
    parser.add_argument("--out-dir", type=Path, default=default_output_dir())
    parser.add_argument("--focal-start-year", type=int, default=None)
    parser.add_argument("--focal-end-year", type=int, default=None)
    parser.add_argument(
        "--max-evidence",
        type=int,
        default=3,
        help="Evidence records to keep per path in the CSV; use 0 for all evidence.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    max_evidence = parse_max_evidence(args.max_evidence)

    run_metadata = build_outputs(
        data_dir=args.data_dir,
        raw_jsonl=args.raw_jsonl,
        semiclean_csv=args.semiclean_csv,
        out_dir=args.out_dir,
        focal_start_year=args.focal_start_year,
        focal_end_year=args.focal_end_year,
        max_evidence=max_evidence,
    )
    print(json.dumps(run_metadata, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
