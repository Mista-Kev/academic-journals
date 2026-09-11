# Results

We compare publication patterns in 27,400 papers from 64 AI journals, covering
2015–2024. The results describe recurrence and associations with first journal
entry. They do not establish causal effects.

## Q1 and Q2: repeat publications

Each ratio divides the observed recurrence rate by the expected rate under the
corresponding random reference model. Both models preserve authors' paper counts
and dates; the second also uses primary topic category when assigning journals.

| Question | Year reference | Year + topic-category reference |
|---|---:|---:|
| Q1: same journal again | 3.09 [3.03, 3.15] | 2.22 [2.18, 2.26] |
| Q2 wide: same publisher, same journal allowed | 2.02 [1.99, 2.05] | 1.69 [1.67, 1.71] |
| Q2 narrow: same publisher through another journal | 1.16 [1.11, 1.20] | 1.11 [1.07, 1.15] |

Brackets show nominal 95% intervals assuming independent authors and fixed journal
weights. We resample whole authors 4,000 times (seed 20260910), using exact null
expectations. The ratios round to the same values as the original 100-run simulation.
We keep journal weights and publisher mapping fixed. Co-author dependence and
uncertainty in the weights are not covered, so 95% coverage for this corpus is not
established. Q2 narrow excludes 1 under these assumptions; accounting for dependence
could change that. The notebook also shows simulated-rate ranges, which are not
confidence intervals for the ratios.

Recurrence exceeds what these particular models predict. That does not establish
loyalty independent of topic. Q2 narrow also overlaps with Q1: 1,468 of its 4,919
cases are journal returns. The remaining 3,451 cases have no separate null comparison.

Pierre's Q1 Intra file describes topic similarity within 9,195 observed
author-journal groups. It sits alongside these ratios; it does not adjust them.
Historical continuous topic adjustment for return opportunities was not built.

## Q3: prior co-author connection and first journal entry

C indicates a qualifying prior co-author connection. T measures historical topic
fit between author and journal. We fit logistic models and average predicted
entry probabilities with C set to 1 and 0 over the same rows. Dividing these averages gives the risk ratio below.

| Outcome | C + T, all complete cases | C + T, matched rows | With journal and year, matched rows |
|---|---:|---:|---:|
| All entries | 6.09 [5.76, 6.45] | 6.01 [5.67, 6.36] | 2.27 [2.13, 2.41] |
| Non-ride entries | 3.34 [3.12, 3.58] | 3.30 [3.08, 3.53] | 1.18 [1.10, 1.27] |

The first column uses 1,106,356 rows with measurable T. The last two use the same
1,088,420 rows. We check for zero events in each outcome and exclude the affected
journals from both models. Here it is one journal with 17,936 rows. The remaining
journals and years must contain events and non-events for both outcomes. This
selection depends on the outcomes. Journal and year enter as separate terms.

Brackets show nominal 95% intervals from the delta method, clustered by author.
They hold the included covariates fixed and assume independent author clusters.
They do not cover co-author dependence, model choice or selection through missing T.

Adding journal and year makes the association much smaller. That is part of the
result. Non-ride means the qualifying earlier co-author is absent from the selected
entry paper, not that we have isolated a direct network effect. Missing T stays
missing, and historical T can already reflect earlier collaboration.

Adding `log1p(n_prior_papers)` gives the following sensitivity results on the same
1,088,420 rows:

| Outcome | C + T + prior paper count | Also with journal and year |
|---|---:|---:|
| All entries | 5.62 [5.33, 5.93] | 2.29 [2.16, 2.43] |
| Non-ride entries | 3.10 [2.90, 3.32] | 1.21 [1.12, 1.30] |

The count includes earlier corpus papers, not just those used in the topic profile.
We use a log term so differences matter less at higher counts; we did not test other
forms. Adding it changes the estimates only slightly. It does not explain away the
association or make T a measure of topic alone: earlier paper counts can already
reflect collaboration. The embeddings stay unchanged.

For my part, I keep the original C+T non-ride result and show the journal/year
result beside it. This is my proposed reporting choice, not a recorded team decision.

## Data and rule checks

The annual table contains 6,422,558 opportunities, 96,819 entries and 1,784 entries
with a qualifying seed, including 756 rides. Python and Prolog agree on the keys
and the connection, entry, ride and non-ride indicators across all rows.
Q3 uses Pierre's official v5 export. Both analyses reproduced their results after
loading the shared files from SharePoint. The comparison checks these indicators, not T or every column.

[Run the analyses](../README.md#how-to-use-it) · [Understand the calculations](../B_opportunities_and_analysis/README.md)

## Choices and history

- **11 September, Q3 sensitivity:** added clustered intervals to the matched-row
  models, checked zero events separately for both outcomes, and added prior corpus
  paper count as a log term. Previously the journal/year models reported only point
  estimates. The original results and reporting choice remain alongside this extension.

- **10 September, Q1/Q2 uncertainty:** retained the simulation ranges and added
  nominal author-bootstrap intervals with exact null expectations, assuming
  independent authors and fixed journal weights.
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
- **10–11 September, shared data:** downloaded the release and checked its files,
  then ran Q1/Q2 and Q3 locally. The full Colab run using SharePoint inputs produced
  an event table identical to the official v5 file. New outputs are in a separate
  SharePoint run folder; downloading them again gave identical files.

The [Python/Prolog report](../B_opportunities_and_analysis/event_table_parity.md)
and [topic results](../C_topic_match/README_results.md) contain the detailed checks.
Earlier plans and chronological development notes remain in
[Git history](https://github.com/Mista-Kev/academic-journals/tree/576e93e/D_results/methods).
The notebook in `archive/` is an old plan, not another runnable analysis.
