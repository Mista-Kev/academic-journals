# Q1–Q3 inputs, calculations and outputs

We use the same paper corpus for three questions: return to a journal, return to
a publisher, and first journal entry with a prior co-author connection.
[Setup and run commands](../DEMO.md) · [Results](../README.md)

## Inputs and outputs

The folders below are relative to the repository root. Large files are supplied
through SharePoint; [the manifest](../../data-manifest.json) lists their full paths.

| Step | Run | Reads → produces |
|---|---|---|
| Q1/Q2 | [q1_q2_baselines.ipynb](../../B_opportunities_and_analysis/q1_q2_baselines.ipynb) | A's semiclean corpus and publisher mapping; pathway flags for comparison → observed rates, simulated expected rates and ratios |
| Q3 opportunities | [build_event_table.py](../../B_opportunities_and_analysis/build_event_table.py) | Same corpus, mapping and flags → `B_opportunities_and_analysis/data/event_table_python_v0_oppA.csv`, plus variant B |
| Independent rule check | [check_event_table_parity.py](../../A_data_and_rules/logic/check_event_table_parity.py) | Prolog facts from A's wrapper → `A_data_and_rules/data/event_table_prolog_v0_oppA.csv`; [diff_event_table.py](../../B_opportunities_and_analysis/diff_event_table.py) compares it with B's table |
| Topic fit | [embeddings_colab_eventtable_v5.ipynb](../../C_topic_match/embeddings_colab_eventtable_v5.ipynb) | B's opportunities and paper histories in Pierre's DuckDB/Colab environment → `C_topic_match/data/event_table_topicmatch_v5.csv`; separate Q1 Intra output in `C_topic_match/results/` |
| Q3 | [q3_baselines.ipynb](../../B_opportunities_and_analysis/q3_baselines.ipynb) | B's annual table, C's official v5 table and historical Min-3 comparison → crude and adjusted risk ratios, intervals and sensitivity results |

Both analysis notebooks display results in the notebook or terminal. They do not
upload new results to SharePoint. `B_opportunities_and_analysis/results/q3_v5/model_results.json`
is a separate reference calculation, not an export from the notebook.

## Q1/Q2: observed recurrence

One observation is an **author-paper pair**. We check the author's publications
on strictly earlier dates. Papers on the same date do not count as history for
each other. All 110,654 pairs remain in the denominator, including first papers.

- **Q1:** earlier publication in the same journal; 12,325 cases.
- **Q2 wide:** earlier publication with the same known parent publisher, including
  the same journal; 15,770 cases.
- **Q2 narrow:** earlier publication in another journal of that publisher; 4,919 cases.

Q2 narrow can still include a return to the current journal: 1,468 cases also
satisfy Q1. The other 3,451 cases have no separate null comparison. Unknown
publishers generate no positive publisher match; those pairs remain in the denominator.

## Q1/Q2: expected recurrence

The notebook's `build_dist` and `null_rates` functions implement two reference
models: journal frequencies by **year**, and by **year plus primary topic category**.
Both Q1 and Q2 use both comparisons.

1. Count each paper once to obtain journal weights within each year or year/topic group.
2. Keep each author's paper count, dates and categories. Assign a journal to every
   author-paper position using those weights, rebuilding the full journal history.
3. Apply the same recurrence rules to that simulated history.
4. Repeat 100 times per model, with random seed 42. Divide the observed rate by
   the mean simulated rate. We do not average the individual ratios.

The draws are **with replacement**: weights stay fixed and a journal can be drawn
again. This models recurrence under independent assignments from the observed
journal distribution. It does not assume a limited number of publication slots.
For example, Q1's observed rate of about 0.1114 divided by the year-model expected
rate of about 0.0361 gives 3.09.

This is a reference model, not a claim that authors actually choose independently.
Journal totals are not fixed exactly in each simulation. Because draws occur per
author-paper pair, co-authors of one paper can receive different simulated journals.
A permutation without replacement could instead preserve journal totals and still
allow recurrence when several slots carry the same journal. That alternative was
not implemented. The 100 simulations estimate the reference rate, not confidence
intervals for the observed ratios.

## Topic categories, historical T and Q1 Intra

Q1/Q2's second reference model accounts for broad topic categories. It does not
use the continuous historical author-journal topic fit **T** used in Q3.
Pierre's **topic_match_intra** describes similarity among papers already published
by an author in one journal; it is a separate descriptive result.

A historical T-adjusted return analysis would need profiles for return opportunities
and alternative journals. Q3's table stops after first entry, so it cannot supply
those return rows. Neither the current ratios nor Intra establish topic-independent loyalty.

## Q3: first entry opportunities

One row is an **author, a journal not previously entered, and a year t**. The
6,422,558 opportunities include non-entries, which provide the denominator.
The main analysis uses opportunity set A; B is a separate table variant.

**C** marks a prior co-author connection to the target journal. The same person
must provide both the earlier collaboration and the earlier journal publication.
**F** marks an entry, derived from `entering_work_id`. **T** compares author and
journal profiles built from papers in years strictly before t. The B and C tables
are checked for identical keys and row order before combining their fields.

We retain continuous T and fit on the 1,106,356 rows where it can be measured.
Missing values remain missing. For each outcome, we fit a logistic model with C
and T, predict every included row with C=1 and C=0 while keeping T unchanged,
and divide the two mean predicted probabilities. This is a standardized risk ratio,
not the odds ratio obtained by exponentiating the C coefficient.

For **non-ride**, the outcome is `first_entry * (1 - first_entry_ride)`. Both
predicted risks come from that outcome's model. Ride rows stay in the population
with outcome zero; we do not filter them out. Non-ride does not mean a direct
network effect: its classification depends on the seed history.

We also add separate journal and year terms. One journal with no entries is
excluded to handle separation, removing 17,936 rows. This is an outcome-based
restriction. On the same remaining 1,088,420 rows, the non-ride ratio changes
from **3.30 to 1.18**; the all-entry ratio changes from **6.01 to 2.27**.
The full complete-case C+T results are 3.34 and 6.09 respectively.

The adjusted intervals use an author-clustered delta method, not the bootstrap
in the earlier plan. This accounts for repeated authors but does not fully cover
shared journal/paper dependence. The attempted two-way covariance estimates were
not positive semidefinite; no new v5 bootstrap refits or bootstrap likelihood-ratio
test are claimed.

The result is sensitive to the model and population. Complete cases are selected,
and pre-t topic profiles may already reflect earlier collaboration. We therefore
report associations, not identified causal effects. The [decision record](decisions.md)
explains the reporting choices; [D](../README.md) gives the results and intervals.
