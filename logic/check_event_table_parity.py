"""Build the Q3 event table from the Prolog rules in event_table_rules.pl.

This is the second, independent implementation of the event table. The driver
only locates SWI-Prolog, runs the rules over the frozen fact file and formats
the emitted lines as CSV. Every event table definition lives in the Prolog
rules, not here.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parent.parent
FACTS_PATH = (
    REPO_ROOT / "results" / "openalex_three_path_v1_0" / "openalex_three_path_facts.pl"
)
RULES_PATH = REPO_ROOT / "logic" / "event_table_rules.pl"
OUTPUT_PATH = REPO_ROOT / "data" / "event_table_prolog_v0_oppA.csv"

COLUMNS = ["author_id", "journal_id", "t", "C", "F", "ride"]

# Cases derived by hand from the corpus before these rules existed. Each entry is
# (author_id, journal_id, t, C, F, ride, entering_work_id).
FIXTURES: tuple[tuple[str, str, int, int, int, int, str], ...] = (
    ("A5000223389", "S2764955546", 2023, 1, 1, 1, "W4385335960"),
    ("A5000042272", "S196734849", 2024, 1, 1, 0, "W4401922468"),
    ("A5028476919", "S155526855", 2017, 1, 1, 0, "W2598515261"),
)


def find_swipl_executable() -> Path:
    configured_path = os.environ.get("SWIPL_PATH")
    if configured_path and Path(configured_path).expanduser().is_file():
        return Path(configured_path).expanduser()
    found = shutil.which("swipl")
    if found:
        return Path(found)
    raise FileNotFoundError("SWI-Prolog not found. Install it or set SWIPL_PATH.")


def prolog_command(executable: Path, goal: str) -> list[str]:
    return [
        str(executable),
        "-q",
        "-s",
        str(FACTS_PATH),
        "-s",
        str(RULES_PATH),
        "-g",
        goal,
    ]


def run_fixtures(executable: Path) -> bool:
    """Check the hand-derived cases before trusting the full enumeration."""
    goal = ", ".join(
        f"emit_case('{author}', '{journal}', {year})"
        for author, journal, year, *_ in FIXTURES
    )
    completed = subprocess.run(
        prolog_command(executable, f"{goal}, halt"),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"SWI-Prolog failed: {completed.stderr.strip()}")

    emitted = [line.split("|") for line in completed.stdout.split() if line]
    all_ok = True
    for expected, fields in zip(FIXTURES, emitted):
        author, journal, year, seed, entry, ride, work_id = expected
        actual = (
            fields[1],
            fields[2],
            int(fields[3]),
            int(fields[4]),
            int(fields[5]),
            int(fields[6]),
            fields[7],
        )
        ok = actual == (author, journal, year, seed, entry, ride, work_id)
        all_ok = all_ok and ok
        print(
            f"fixture {'PASS' if ok else 'FAIL'} "
            f"{author} {journal} {year} "
            f"C={actual[3]} F={actual[4]} ride={actual[5]} entering={actual[6]}"
        )
        if not ok:
            print(f"  expected C={seed} F={entry} ride={ride} entering={work_id}")
    if len(emitted) != len(FIXTURES):
        print(f"fixture FAIL: expected {len(FIXTURES)} cases, got {len(emitted)}")
        all_ok = False
    return all_ok


def build_event_table(executable: Path, output_path: Path) -> dict[str, int]:
    """Stream the Prolog rows into a CSV and count the totals while doing it."""
    totals = {
        "rows": 0,
        "seeded_rows": 0,
        "entries": 0,
        "seeded_entries": 0,
        "rides": 0,
    }
    process = subprocess.Popen(
        prolog_command(executable, "emit_event_table, halt"),
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1024 * 1024,
    )
    assert process.stdout is not None
    with output_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for line in process.stdout:
            fields = line.rstrip("\n").split("|")
            if fields[0] != "ROW":
                raise ValueError(f"unexpected Prolog output: {line!r}")
            author, journal, year, seed, entry, ride = fields[1:]
            writer.writerow((author, journal, year, seed, entry, ride))
            totals["rows"] += 1
            totals["seeded_rows"] += seed == "1"
            totals["entries"] += entry == "1"
            totals["seeded_entries"] += seed == "1" and entry == "1"
            totals["rides"] += ride == "1"
    if process.wait() != 0:
        raise RuntimeError(f"SWI-Prolog failed with exit code {process.returncode}.")
    return totals


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument(
        "--fixtures-only",
        action="store_true",
        help="Only check the hand-derived cases and stop.",
    )
    args = parser.parse_args(argv)

    executable = find_swipl_executable()
    if not run_fixtures(executable):
        print("Fixtures failed, not building the table.", file=sys.stderr)
        return 1
    if args.fixtures_only:
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    totals = build_event_table(executable, args.output)
    elapsed = time.monotonic() - started

    print(f"\nwrote {args.output}")
    print(f"runtime {elapsed:.1f}s")
    for name, value in totals.items():
        print(f"{name}: {value:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
