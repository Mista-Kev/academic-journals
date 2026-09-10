# Results

We compare publication patterns in 27,400 papers from 64 AI journals, covering
2015–2024. The results describe recurrence and associations with first journal
entry. They do not establish causal effects.

## Q1 and Q2: observed recurrence versus expected recurrence

Each ratio divides the observed recurrence rate by the mean rate from the
corresponding random reference model. Both models preserve authors' paper counts
and dates; the second also uses primary topic category when assigning journals.

| Question | Year reference | Year + topic-category reference |
|---|---:|---:|
| Q1: same journal again | 3.09 | 2.22 |
| Q2 wide: same publisher, same journal allowed | 2.02 | 1.69 |
| Q2 narrow: same publisher through another journal | 1.16 | 1.11 |

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
remains proposed in the [decision record](methods/decisions.md).

## Data and rule checks

The annual table contains 6,422,558 opportunities, 96,819 entries and 1,784 entries
with a qualifying seed, including 756 rides. Python and Prolog agree on all rows.
Q3 uses Pierre's official v5 export. Both analyses reproduced their results after
loading the shared files from SharePoint. These checks establish agreement of the
files and calculations, not causal validity.

[Run the analyses](DEMO.md) · [Understand the calculations](methods/analysis-interfaces.md) · [Check record](methods/validation.md)
