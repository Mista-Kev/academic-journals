"""Compare the Prolog event table against the Python event table build.

The comparison is a merge join on (author_id, journal_id, t). Both sides are
projected to the same six columns, sorted with the C collation and then walked
in lockstep, so neither table has to be held in memory.

This script is the only place in the Prolog implementation that reads the
Python build. It was written after the Prolog rules were committed.
"""

from __future__ import annotations

import argparse
import csv
import errno
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Iterator, Sequence


REPO_ROOT = Path(__file__).resolve().parent.parent
PROLOG_PATH = REPO_ROOT / "A_data_and_rules" / "data" / "event_table_prolog_v0_oppA.csv"
PYTHON_PATH = REPO_ROOT / "B_opportunities_and_analysis" / "data" / "event_table_python_v0_oppA.csv"

PYTHON_COLUMNS = (
    "author_id",
    "journal_id",
    "t",
    "coauthor_seed",
    "first_entry_independent",
    "first_entry_ride",
    "entering_work_id",
)
TRUE_VALUES = {"1", "1.0", "true", "True", "TRUE"}
FALSE_VALUES = {"0", "0.0", "false", "False", "FALSE", ""}
MAX_EXAMPLES = 10


def as_flag(value: str, column: str) -> str:
    text = value.strip()
    if text in TRUE_VALUES:
        return "1"
    if text in FALSE_VALUES:
        return "0"
    raise ValueError(f"unexpected value {value!r} in column {column}")


def project_prolog(source: Path, target: Path) -> dict[str, int]:
    """Copy the Prolog table into key/flag lines and count its totals."""
    totals = dict.fromkeys(("rows", "seeded_rows", "entries", "seeded_entries", "rides"), 0)
    with source.open(newline="") as handle, target.open("w") as out:
        reader = csv.DictReader(handle)
        for row in reader:
            seed, entry, ride = row["C"], row["F"], row["ride"]
            out.write(
                f"{row['author_id']}\t{row['journal_id']}\t{row['t']}"
                f"\t{seed}\t{entry}\t{ride}\n"
            )
            totals["rows"] += 1
            totals["seeded_rows"] += seed == "1"
            totals["entries"] += entry == "1"
            totals["seeded_entries"] += seed == "1" and entry == "1"
            totals["rides"] += ride == "1"
    return totals


def project_python(source: Path, target: Path) -> dict[str, int]:
    """Copy the Python table into the same key/flag lines and count its totals.

    F is read from entering_work_id as specified. The independent/ride pair is checked
    row by row against independent = F and not ride, which covers both the complement
    and the exclusivity of the two entry flags.
    """
    totals = dict.fromkeys(
        ("rows", "seeded_rows", "entries", "seeded_entries", "rides", "outcome_split_disagreements"),
        0,
    )
    with source.open(newline="") as handle, target.open("w") as out:
        reader = csv.DictReader(handle)
        missing = [name for name in PYTHON_COLUMNS if name not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing columns in {source}: {', '.join(missing)}")
        for row in reader:
            seed = as_flag(row["coauthor_seed"], "coauthor_seed")
            ride = as_flag(row["first_entry_ride"], "first_entry_ride")
            independent = as_flag(row["first_entry_independent"], "first_entry_independent")
            entry = "1" if row["entering_work_id"].strip() else "0"
            # the split must be exact, independent is entry without a ride, so both flags can never be 1 at once
            if independent != ("1" if entry == "1" and ride == "0" else "0"):
                totals["outcome_split_disagreements"] += 1
            out.write(
                f"{row['author_id']}\t{row['journal_id']}\t{row['t']}"
                f"\t{seed}\t{entry}\t{ride}\n"
            )
            totals["rows"] += 1
            totals["seeded_rows"] += seed == "1"
            totals["entries"] += entry == "1"
            totals["seeded_entries"] += seed == "1" and entry == "1"
            totals["rides"] += ride == "1"
    return totals


def sort_file(path: Path, target: Path, tmp_dir: Path) -> None:
    with target.open("w") as out:
        subprocess.run(
            ["sort", "-T", str(tmp_dir), str(path)],
            stdout=out,
            stderr=subprocess.PIPE,
            text=True,
            env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"},
            check=True,
        )


def read_sorted(path: Path) -> Iterator[tuple[str, tuple[str, str, str]]]:
    with path.open() as handle:
        for line in handle:
            author, journal, year, seed, entry, ride = line.rstrip("\n").split("\t")
            yield f"{author}\t{journal}\t{year}", (seed, entry, ride)


def compare(prolog_sorted: Path, python_sorted: Path) -> dict[str, object]:
    """Merge join both sorted projections and describe every difference."""
    left, right = read_sorted(prolog_sorted), read_sorted(python_sorted)
    result: dict[str, object] = {
        "shared_keys": 0,
        "only_prolog": 0,
        "only_python": 0,
        "flag_mismatches": {"C": 0, "F": 0, "ride": 0},
        "examples": [],
        "duplicate_keys": 0,
    }
    a, b = next(left, None), next(right, None)
    last_a = last_b = None
    while a is not None or b is not None:
        if b is None or (a is not None and a[0] < b[0]):
            result["only_prolog"] += 1
            add_example(result, "only in prolog", a[0], a[1], None)
            last_a, a = a[0], next(left, None)
        elif a is None or b[0] < a[0]:
            result["only_python"] += 1
            add_example(result, "only in python", b[0], None, b[1])
            last_b, b = b[0], next(right, None)
        else:
            result["shared_keys"] += 1
            if a[1] != b[1]:
                for index, name in enumerate(("C", "F", "ride")):
                    if a[1][index] != b[1][index]:
                        result["flag_mismatches"][name] += 1
                add_example(result, "flag mismatch", a[0], a[1], b[1])
            if a[0] == last_a or b[0] == last_b:
                result["duplicate_keys"] += 1
            last_a, last_b = a[0], b[0]
            a, b = next(left, None), next(right, None)
    return result


def add_example(
    result: dict[str, object],
    kind: str,
    key: str,
    prolog_flags: tuple[str, str, str] | None,
    python_flags: tuple[str, str, str] | None,
) -> None:
    examples = result["examples"]
    if len(examples) < MAX_EXAMPLES:
        examples.append((kind, key, prolog_flags, python_flags))


def report(prolog_totals, python_totals, result) -> bool:
    print("Prolog event table totals")
    for name, value in prolog_totals.items():
        print(f"  {name}: {value:,}")

    print("\nPython event table totals")
    for name, value in python_totals.items():
        print(f"  {name}: {value:,}")

    print("\nComparison on (author_id, journal_id, t)")
    print(f"  keys in both: {result['shared_keys']:,}")
    print(f"  only in prolog: {result['only_prolog']:,}")
    print(f"  only in python: {result['only_python']:,}")
    print(f"  duplicate keys seen: {result['duplicate_keys']:,}")
    for name, count in result["flag_mismatches"].items():
        print(f"  {name} mismatches: {count:,}")

    if result["examples"]:
        print(f"\nFirst {len(result['examples'])} differences")
        for kind, key, prolog_flags, python_flags in result["examples"]:
            print(f"  {kind} {key} prolog={prolog_flags} python={python_flags}")

    clean = (
        result["only_prolog"] == 0
        and result["only_python"] == 0
        and result["duplicate_keys"] == 0
        and not any(result["flag_mismatches"].values())
        and python_totals.get("outcome_split_disagreements", 0) == 0
    )
    print("\nVERDICT: " + ("identical" if clean else "MISMATCH"))
    return clean


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prolog", type=Path, default=PROLOG_PATH)
    parser.add_argument("--python", type=Path, default=PYTHON_PATH)
    parser.add_argument("--temp-dir", type=Path,
                        help="Existing directory with space for projections and external sorting")
    args = parser.parse_args(argv)

    if sys.platform == "win32":
        print("This comparison requires Unix sort with -T; native Windows sort is incompatible. "
              "Use the documented macOS environment. WSL is not tested.", file=sys.stderr)
        return 2

    started = time.monotonic()
    temp_root = args.temp_dir
    try:
        if temp_root is None:
            temp_root = Path(tempfile.gettempdir())
        # Budget for both projections, sorted copies and sort's scratch files.
        # This is a conservative reserve, not an exact peak-space prediction.
        reserve = max(16 * 1024**2, 4 * (args.prolog.stat().st_size + args.python.stat().st_size))
        free = shutil.disk_usage(temp_root).free
        if free < reserve:
            print(f"Not enough temporary disk space in {temp_root}: {free / 1024**3:.2f} GiB free; "
                  f"reserve {reserve / 1024**3:.2f} GiB for this comparison. "
                  "Free space or select an existing folder on another disk with --temp-dir. "
                  "No comparison was run.", file=sys.stderr)
            return 2
        with tempfile.TemporaryDirectory(prefix="event-table-diff-", dir=temp_root) as tmp_name:
            tmp_dir = Path(tmp_name)
            prolog_totals = project_prolog(args.prolog, tmp_dir / "prolog.tsv")
            python_totals = project_python(args.python, tmp_dir / "python.tsv")
            sort_file(tmp_dir / "prolog.tsv", tmp_dir / "prolog.sorted", tmp_dir)
            sort_file(tmp_dir / "python.tsv", tmp_dir / "python.sorted", tmp_dir)
            result = compare(tmp_dir / "prolog.sorted", tmp_dir / "python.sorted")
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()
        print(f"External sort failed (exit {exc.returncode}). {detail}\n"
              f"Check free space and write access in {temp_root}; "
              "use --temp-dir for another disk. No comparison verdict is available.", file=sys.stderr)
        return 2
    except OSError as exc:
        if temp_root is None:
            print("Could not find a usable default temporary directory. Check free space and "
                  "write access, or select an existing writable folder with --temp-dir. "
                  "No comparison was run.", file=sys.stderr)
        elif exc.errno == errno.ENOSPC:
            print(f"Disk filled during comparison in {temp_root}. Free space or use --temp-dir "
                  "on another disk, then rerun. No comparison verdict is available.", file=sys.stderr)
        else:
            print(f"Could not compare the tables: {exc}. Check the input paths and temporary "
                  "directory permissions. No comparison verdict is available.", file=sys.stderr)
        return 2

    clean = report(prolog_totals, python_totals, result)
    print(f"comparison runtime {time.monotonic() - started:.1f}s")
    return 0 if clean else 1


if __name__ == "__main__":
    raise SystemExit(main())
