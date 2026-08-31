# logic/ — event layer

**Purpose:** derive the events behind the three questions. Two layers: the pathway rules (`openalex_three_path_rules.pl` + Python wrapper, day-level, one row per published author-paper pair) and the Q3 event table (year-level, one row per (author, journal, year) opportunity, built by `build_event_table.py`). The pathway flags were rebuilt independently in Python and matched on all 110,654 rows; an independent Prolog counterpart of the event table exists for the same cross-check.
**Owner:** Lennart (rules), Kevin (Python counterparts)
**Input:** the semiclean corpus from `data/`, generated facts in `results/`
**Output:** pathway flags in `results/`, event table CSVs in `data/` (gitignored)
