# nets/ — Bayes nets & metrics

**Purpose:** three small (3-node) Bayes nets in bn-logtalk: variable elimination, d-separation, do-operator, EM for soft labels. Delivers Q1 (repeat ratio), Q2 (publisher excess), Q3 (co-author factor = P1 ÷ P0).
**Owner:** Kevin
**Input:** event table from `logic/` + `topic_match` from `topics/`
**Output:** metrics Q1/Q2/Q3 for `stats/` and `report/`
