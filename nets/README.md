# nets/ — analysis notebooks

**Purpose:** the question-level analyses. `q1_q2_baselines.ipynb` answers Q1 and Q2 as observed over expected against explicit chance models. `q3_planning.ipynb` works out the Q3 design on a hand-built toy table. `q3_baselines.ipynb` runs Q3 on the real event table: crude contrast with author-clustered intervals, missingness audit for `topic_match`, and a provisional topic-adjusted ratio via logistic regression and g-computation.
**Owner:** Kevin
**Input:** event table from `logic/`, `topic_match` from `topics/`
**Output:** the Q1/Q2/Q3 numbers for `report/`
