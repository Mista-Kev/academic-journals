# Running and explaining the analyses

Follow the [data setup](methods/shared-data.md#how-to-use-it) once, then run from
the repository root:

```sh
python3 demo.py q1-q2
python3 demo.py q3
```

These commands execute every Python cell in the corresponding notebooks and print
fresh results in the terminal. They leave saved notebook outputs unchanged.
No new OpenAlex download or GPU run is needed. For the notebook view, open the
files in B and use B as the kernel's working directory.

## What to look at

- **Q1/Q2:** observed recurrence, expected recurrence under each reference model,
  and their ratio. Explain what changes when the comparison includes topic category.
- **Q3:** an author-journal-year opportunity, including rows without entry; the
  prior co-author connection C; and historical topic fit T, where available.
- **Results:** compare C+T with the journal/year sensitivity. For non-ride entries,
  the comparison on identical rows is **3.30 → 1.18**. The full complete-case
  estimate is **3.34**. [D explains the populations and interpretation](README.md).

For a group walkthrough, Lennart explains the papers and publication rules,
Pierre explains the topic profiles, and Kevin explains the comparison groups and
calculations. Finish with what the results support and what remains uncertain.
[The analysis description](methods/analysis-interfaces.md) provides the reasoning.

## Optional: compare the Python and Prolog tables

```sh
python3 project_data.py fetch --group parity
python3 B_opportunities_and_analysis/diff_event_table.py
```

This compares the existing annual tables. It checks whether both implementations
produce the same rows and flags, not whether the research interpretation is causal.

<details>
<summary>Software tests and rebuilding the tables</summary>

Run all tests from the repository root:

```sh
python3 -m unittest discover -s . -v
```

Or just the loader and builder tests:

```sh
python3 -m unittest discover -s B_opportunities_and_analysis/tests -p 'test_*.py' -v
```

Tests use small fixtures. Git is needed for the line-ending check; SWI-Prolog is
needed for the Prolog integration tests, which are skipped if it is absent.

To rebuild both full tables, install SWI-Prolog and use a separate checkout
because these commands write derived files:

```sh
python3 project_data.py fetch --group corpus
python3 A_data_and_rules/logic/openalex_three_path_prolog.py --data-dir A_data_and_rules/data --out-dir A_data_and_rules/results/openalex_three_path_v1_0
python3 B_opportunities_and_analysis/build_event_table.py
python3 A_data_and_rules/logic/check_event_table_parity.py --fixtures-only
python3 A_data_and_rules/logic/check_event_table_parity.py
python3 B_opportunities_and_analysis/diff_event_table.py
python3 project_data.py verify --group parity
```

The last command checks file hashes as well. Different Prolog serialization can
produce different bytes even when the rows agree. Investigate a mismatch rather
than changing the manifest hash to accept it.

</details>

Rebuilding C's embeddings requires its separate DuckDB/Colab/GPU setup. The
current Q3 analysis is regression with standardization; it is not runnable
Bayes-net software.
