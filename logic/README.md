# logic/ — event layer

**Purpose:** derive the events behind the three questions. The pathway layer (`openalex_three_path_rules.pl` plus its Python wrapper) is day-level and has one row per published author-paper pair. The Q3 event table is year-level and has one row per `(author, journal, year)` opportunity, including opportunities without an entry. Independent implementations are used to check the key pathway and Q3 flags.
**Owner:** Lennart (rules), Kevin (Python counterparts)
**Input:** the semiclean corpus from `data/`, generated pathway facts in `results/`
**Output:** pathway flags in `results/`, event table CSVs in `data/` (gitignored)
