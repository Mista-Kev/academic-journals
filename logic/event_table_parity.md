# Event table parity result

Date: 2026-08-30

Two independent implementations of the Q3 event table were compared row by row.

- Python build: `logic/build_event_table.py`, output `data/event_table_python_v0_oppA.csv`
  sha256 `76f5ed2b37a4f683ac4c754e195417e65352155f3bcc4349f626252e34b6a041`
- Prolog build: `logic/event_table_rules.pl` via `logic/check_event_table_parity.py`,
  output `data/event_table_prolog_v0_oppA.csv`
  sha256 `28d31995d63856001eac8f174f7cf0d7101ccc66d0892e5350c758e091ca1f3d`

Comparison command: `python3 logic/diff_event_table.py`

Result

- 6,422,558 keys `(author_id, journal_id, t)` present in both outputs, none only on one side, no duplicates
- 0 mismatches on `C`, 0 on `F`, 0 on `ride`
- shared totals: 19,035 seeded rows, 96,819 entries, 1,784 seeded entries, 756 rides

The Prolog rules were written from the schema text without consulting the Python
implementation; review of the rules against the written definitions is the remaining step.
Both output CSVs are gitignored build products and are reproduced by the commands above.
