# logic

## Purpose

Build the temporal publication paths and the Q3 event table.

The logic layer uses publication history inside the frozen corpus. Evidence must be strictly earlier than the focal publication.

## Part 1: Publication pathways

### Run

Run the notebook, or depending on your input/output folders the following could work as well:

```powershell
python logic/openalex_three_path_prolog.py --data-dir data --out-dir results/openalex_three_path_v1_0
```

Use `--raw-jsonl` and `--semiclean-csv` when the files are stored elsewhere.

Optional arguments:

- `--focal-start-year YEAR`
- `--focal-end-year YEAR`
- `--max-evidence N`

Use `--max-evidence 0` to keep all evidence records.

### What the wrapper does

1. Load the raw JSONL.
2. Resolve the parent publisher from the OpenAlex lineage.
3. Load the semiclean CSV.
4. Normalize IDs and authorships.
5. Write Prolog facts.
6. Run the Prolog rules.
7. Parse the results.
8. Write the output CSV files.

### Path definitions

- `journal_path`: the author published earlier in the same journal.
- `publisher_path`: the author published earlier in another journal with the same known parent publisher.
- `coauthor_path`: another author of the focal work published earlier in the focal journal.

All three paths use strict publication-date order. Unknown parent publishers do not create a publisher path.

### Output

The selected output directory contains:

- `journal_parent_publishers.csv`
- `openalex_three_path_facts.pl`
- `openalex_three_path_rules.pl`
- `pathway_results.csv`
- `pathway_flags.csv`
- `pathway_evidence.csv`

`pathway_flags.csv` has one row per focal author-work pair. The evidence file lists the earlier works behind each flag.

## Part 2: Q3 event table

### Prerequisites

Run the pathway wrapper first. The event-table builder needs:

- `data/openalex_ai_semiclean_v1_0.csv`
- `results/openalex_three_path_v1_0/journal_parent_publishers.csv`
- `results/openalex_three_path_v1_0/pathway_flags.csv`

### Run

```powershell
python logic/build_event_table.py
```

The script writes two files to `data/`:

- `event_table_python_v0_oppA.csv`: all eligible journal opportunities
- `event_table_python_v0_oppB.csv`: topic-restricted opportunities

Use variant A as the main table. Use variant B as a sensitivity analysis.

### Event-table columns

The table has one row per `(author_id, journal_id, t)` opportunity.

- `coauthor_seed`: an earlier coauthor had already published in the journal
- `t_first_seed`: the first year in which both seed conditions were satisfied
- `first_entry_independent`: first entry without a qualifying seeder on the entering paper, including entries with no seed
- `first_entry_ride`: first entry with a qualifying seeder on the entering paper
- `entering_work_id`: the selected first-entry paper in year `t`
- `topic_match`: left empty for the topic-matching step

`first_entry_independent` and `first_entry_ride` are mutually exclusive outcomes. They are both false on non-entry rows.

### Handoff

Pass the event table to the topic-matching layer. There `topic_match` is added and it then returns the event-table-aligned file for Q3.

## Validation

You can run the logic tests from the repository root:

```powershell
python -m unittest discover -s logic/tests -v
```

The tests cover CSV loading, ID normalization, strict time ordering, publisher mapping, pathway evaluation, and the Prolog integration.

The extended rule file `event_table_rules_with_independent.pl` keeps the original six-field event output and provides a separate output with `first_entry_independent`. The normal Python event-table command remains the main reproducible entry point.
