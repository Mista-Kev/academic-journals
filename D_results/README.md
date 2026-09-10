# Results

We compare publication patterns in 27,400 papers from 64 AI journals, covering
2015–2024. The results describe recurrence and associations with first journal
entry. They do not establish causal effects.

## Q1 and Q2: observed recurrence versus expected recurrence

Each ratio divides the observed recurrence rate by the expected rate under the
corresponding random reference model. Both models preserve authors' paper counts
and dates; the second also uses primary topic category when assigning journals.

| Question | Year reference | Year + topic-category reference |
|---|---:|---:|
| Q1: same journal again | 3.09 [3.03, 3.15] | 2.22 [2.18, 2.26] |
| Q2 wide: same publisher, same journal allowed | 2.02 [1.99, 2.05] | 1.69 [1.67, 1.71] |
| Q2 narrow: same publisher through another journal | 1.16 [1.11, 1.20] | 1.11 [1.07, 1.15] |

Brackets are conditional 95% percentile confidence intervals from 4,000 whole-author
bootstrap samples (seed 20260910). The denominator uses the exact expectation under
the same null; all ratios round to the original 100-run estimates above. Journal
weights and publisher mapping stay fixed. Dependence between coauthors and uncertainty
in those weights are not covered. These are not the ranges of simulated null rates;
the notebook reports those separately. Both narrow intervals exclude 1 under these
assumptions, so being close to 1 should not be read as an absence of excess recurrence.

Recurrence exceeds what these particular models predict. That does not establish
loyalty independent of topic. Q2 narrow also overlaps with Q1: 1,468 of its 4,919
cases are journal returns. The remaining 3,451 cases have no separate null comparison.

Pierre's Q1 Intra file describes topic similarity within 9,195 observed
author-journal groups. It sits alongside these ratios; it does not adjust them.
Historical continuous topic adjustment for return opportunities was not built.

## Q3: prior co-author connection and first journal entry

C indicates a qualifying prior co-author connection. T measures historical topic
fit between author and journal. We fit logistic models and average predicted
entry probabilities with C set to 1 and 0 over the same rows. Their ratio is the
model-standardized risk ratio.

| Outcome | C + T, all complete cases | C + T, matched rows | With journal and year, matched rows |
|---|---:|---:|---:|
| All entries | 6.09 [5.76, 6.45] | 6.01 | 2.27 |
| Non-ride entries | 3.34 [3.12, 3.58] | 3.30 | 1.18 |

The first column uses **1,106,356 rows with measurable T**. The last two use the
same **1,088,420 rows**, excluding 17,936 rows from a journal with no entries to
handle separation. That exclusion depends on the outcome. Journal and year are
separate additive terms. The brackets give 95% author-clustered delta intervals.

**The association becomes much smaller after adding journal and year.** That
model dependence is part of the finding. Non-ride means the qualifying seed
co-author is absent from the selected entry paper; it does not mean a direct
network effect. Missing T remains missing, so adjusted results concern complete
cases. Rolling T can already reflect earlier collaboration.

For Kevin's part, the original C+T non-ride comparison remains the headline,
always shown with the journal/year sensitivity. Adoption in the joint report
remains proposed; this is not recorded as a joint team decision.

## Data and rule checks

The annual table contains 6,422,558 opportunities, 96,819 entries and 1,784 entries
with a qualifying seed, including 756 rides. Python and Prolog agree on all rows.
Q3 uses Pierre's official v5 export. Both analyses reproduced their results after
loading the shared files from SharePoint. These checks establish agreement of the
files and calculations, not causal validity.

[Run the analyses](../README.md#how-to-use-it) · [Understand the calculations](../B_opportunities_and_analysis/README.md)

## Choices and history

- **10 September, Q1/Q2 uncertainty:** retained the simulation ranges and added
  conditional author-bootstrap confidence intervals with exact null expectations.
  Previously only the simulated means were reported; no methodological reason
  for omitting uncertainty had been recorded.
- **July plan:** proposed Bayes nets/Logtalk and causal interpretation. The delivered
  Q3 analysis uses logistic regression with standardization. No direct or total
  causal effect, or upper/lower causal bound, has been identified.
- **August implementation:** annual opportunities provide a common time window
  for entries and non-entries. 28.6% of corpus dates are January 1; this raises
  concerns about daily precision but does not prove every such date was invented.
  Q1/Q2 retain strict date ordering. A separately aligned daily Q3 design was not built.
- **8 August comparison:** non-ride with T was recorded as the main comparison,
  with author bootstrap planned. The current adjusted intervals use clustered delta
  calculations instead. The old entry's title is not proof of preregistration of
  all present specifications.
- **7 September v5:** removed the additional whole-period three-paper threshold
  and built journal profiles from the full embeddable corpus. Later productivity
  should not decide whether earlier histories are eligible. The official export
  and local regeneration agree in non-T fields; T differs by at most about 4.7e-7.
- **9 September reporting choice:** keep the original non-ride C+T comparison and
  show the journal/year result beside it. This preserves the comparison's history,
  not proof that its adjustment set is sufficient. Complete cases define the adjusted
  population; missing T is neither zero-coded nor imputed.
- **Scope:** Q1/Q2 remain descriptive. Historical T-adjusted return models, a daily
  Q3 design and imputation would be additional analyses. A profile frozen at first
  seed lacks a comparable anchor for C=0. These are limitations and alternatives,
  not completed tests.
- **10 September delivery:** all 13 data files and four metadata files were downloaded
  again and matched their sizes and hashes. Full Q1/Q2 and Q3 runs matched previous
  outputs. Three non-analysis downloads were then discarded to save local space;
  the retained local download folder is incomplete. The complete prepared release
  was verified separately. Recipient-account access and automatic OneDrive sync
  were not tested.

The [Python/Prolog report](../B_opportunities_and_analysis/event_table_parity.md)
and [topic results](../C_topic_match/README_results.md) contain the detailed checks.
Earlier plans and chronological development notes remain in
[Git history](https://github.com/Mista-Kev/academic-journals/tree/576e93e/D_results/methods).
The notebook in `archive/` is an old plan, not another runnable analysis.
