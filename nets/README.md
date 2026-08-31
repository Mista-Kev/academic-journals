# nets/ — analysis notebooks

**Purpose:** the question-level analyses. `q1_q2_baselines.ipynb` answers Q1 and Q2 as observed over expected against explicit chance models. `q3_planning.ipynb` develops the Q3 design on a hand-built toy table. The draft `q3_baselines.ipynb` applies it to the real event table with an author-clustered crude contrast, a `topic_match` missingness audit, and a provisional topic-adjusted ratio. The adjusted result is not final while the topic pipeline and missing-value treatment remain under review.
**Owner:** Kevin
**Input:** event table from `logic/`, `topic_match` from `topics/`
**Output:** reviewed Q1/Q2 results and provisional Q3 results for `report/`
