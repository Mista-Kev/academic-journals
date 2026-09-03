# Author loyalty in open-access AI journals

This project studies publication patterns in a frozen OpenAlex corpus of 27,400 papers from 64 open-access AI and computer-science journals between 2015 and 2024. Histories are corpus-internal: publications outside these journals or before 2015 are not observed.

## Questions

- **Q1:** Do authors return to the same journal more often than expected by chance?
- **Q2:** Does that loyalty extend to the journal's parent publisher?
- **Q3:** Is an earlier co-author connection associated with first entry into a journal after accounting for prior topic fit?

Q1 and Q2 are implemented in `nets/q1_q2_baselines.ipynb`. Q3 uses an annual opportunity table with one row per `(author, journal, year)`. Its topic-adjusted results remain provisional while the topic pipeline and missing-value treatment are under review.

## Folders

| Folder | Contents |
|---|---|
| `fetch/` | Corpus retrieval and preparation |
| `data/` | Local generated data and tracked schemas |
| `logic/` | Pathway and event definitions |
| `topics/` | Topic-fit calculation and diagnostics |
| `nets/` | Q1, Q2, and Q3 analysis notebooks |
| `results/` | Tracked reproducibility outputs |
| `stats/` | Statistical checks and sensitivity analyses |
| `report/` | Report and presentation material |
| `docs/` | Decisions, collaboration notes, and historical planning material |

Generated data and local environments are gitignored. Missing `topic_match` means unknown, never zero. Results are described as associations unless the design supports a stronger interpretation.

`docs/plan.md` and `docs/research-notes.md` are retained as historical pre-implementation documents, not as the current specification.
