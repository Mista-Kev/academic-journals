# A · Regeln und unabhängige Gegenprüfung

**Verantwortlich:** Lennart (Prolog-Regeln); Kevin (Python-Gegenstücke).
Die Eingabe ist der Korpus in `../data/`. Der Wrapper
`openalex_three_path_prolog.py` und `openalex_three_path_rules.pl` erzeugen die
Publikationspfade pro Autor-Paper-Paar mit strikt früheren Datumsangaben.
Die Ergebnisse und Fakten liegen bei Verwendung der Demo-Befehle unter
`../results/openalex_three_path_v1_0/`.

`check_event_table_parity.py` und `event_table_rules.pl` erzeugen unabhängig
jährliche Autor-Journal-Gelegenheiten einschließlich Nicht-Eintritten. Die Ausgabe
liegt in `../data/event_table_prolog_v0_oppA.csv`. Der Python-Builder und der
Vollvergleich stehen in `../../B_opportunities_and_analysis/`.

[Ausführen und prüfen](../../D_results/DEMO.md) · [Aktuelle Jahresdefinitionen](../../B_opportunities_and_analysis/schemas/event_table.md)

## Running the rules and event-table handoff

## Purpose

Build the temporal publication paths and the Q3 event table.

The logic layer uses publication history inside the frozen corpus. Paper-level evidence must be strictly earlier than the focal publication.
Annual Q3 evidence must come from years strictly before the considered year `t`.

## Part 1: Publication pathways

### Run

With Python and SWI-Prolog installed and the shared inputs configured, run from the repository root:

```powershell
python project_data.py fetch --group corpus
python A_data_and_rules/logic/openalex_three_path_prolog.py --data-dir A_data_and_rules/data --out-dir A_data_and_rules/results/openalex_three_path_v1_0
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

- `A_data_and_rules/data/openalex_ai_semiclean_v1_0.csv`
- `A_data_and_rules/results/openalex_three_path_v1_0/journal_parent_publishers.csv`
- `A_data_and_rules/results/openalex_three_path_v1_0/pathway_flags.csv`

### Run

```powershell
python B_opportunities_and_analysis/build_event_table.py
```

The script writes two files to `B_opportunities_and_analysis/data/`:

- `event_table_python_v0_oppA.csv`: all eligible journal opportunities
- `event_table_python_v0_oppB.csv`: topic-restricted opportunities

Use variant A as the main table. Use variant B as a sensitivity analysis.

### Event-table columns

The table has one row per `(author_id, journal_id, t)` opportunity.

- `coauthor_seed`: an earlier coauthor had already published in the journal
- `t_first_seed`: first year both seed conditions are known to hold in the observed history; it can be in the future on unseeded opportunity rows, so it is not itself an available predictor at `t`
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
python -m unittest discover -s A_data_and_rules/logic/tests -v
```

The tests cover CSV loading, ID normalization, strict time ordering, publisher mapping, pathway evaluation, and the Prolog integration.

The annual Prolog cross-check uses the tracked `event_table_rules.pl` and
`check_event_table_parity.py`, described above. No additional independent-outcome
rule file is included in this repository. The Python event-table command writes
`first_entry_independent`; the current definitions are in
[the event-table schema](../../B_opportunities_and_analysis/schemas/event_table.md).
