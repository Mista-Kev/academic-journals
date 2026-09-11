# B · Opportunities and analysis

This is where I calculate Q1, Q2 and Q3. Q1/Q2 look at repeat publications.
Q3 looks at first journal entries, including opportunities where no entry happens.

[Setup and commands](../README.md#how-to-use-it) · [Results](../D_results/README.md)

## Files we use

Large files come from SharePoint. The paths follow the same A/B/C folders as this repo.

| Step | Run | Reads → produces |
|---|---|---|
| Q1/Q2 | [q1_q2_baselines.ipynb](q1_q2_baselines.ipynb) | A's semiclean corpus and publisher mapping; pathway flags for comparison → observed rates, simulated expected rates and ratios |
| Q3 opportunities | [build_event_table.py](build_event_table.py) | Same corpus, mapping and flags → `B_opportunities_and_analysis/data/event_table_python_v0_oppA.csv`, plus variant B |
| Independent rule check | [check_event_table_parity.py](../A_data_and_rules/logic/check_event_table_parity.py) | Prolog facts from A's wrapper → `A_data_and_rules/data/event_table_prolog_v0_oppA.csv`; [diff_event_table.py](diff_event_table.py) compares it with B's table |
| Topic fit | [embeddings_colab_eventtable_v5.ipynb](../C_topic_match/embeddings_colab_eventtable_v5.ipynb) | B's opportunities and raw paper data, uploaded to Colab → `C_topic_match/data/event_table_topicmatch_v5.csv`; separate Q1 Intra output in `C_topic_match/results/` |
| Q3 | [q3_baselines.ipynb](q3_baselines.ipynb) | B's annual table, C's official v5 table and historical Min-3 comparison → crude and adjusted risk ratios, intervals and sensitivity results |


The notebooks show their results when you run them. They do not upload them.
`results/q3_v5/model_results.json` is a separate reference calculation, not a notebook export.

## Q1/Q2: what we count

We look at each author-paper pair separately. Co-authors can have different histories.
Only papers with an earlier publication date count; papers on the same date do not
count as history for each other. All 110,654 pairs stay in the denominator, including
first papers.

- Q1: an earlier paper in the same journal. We count 12,325 cases.
- Q2 wide: an earlier paper with the same parent publisher, including the same
  journal. We count 15,770 cases.
- Q2 narrow: an earlier paper in another journal of that publisher. We count 4,919
  cases. Of these, 1,468 are also Q1 returns. We have not calculated a separate null
  comparison for the other 3,451.

An unknown publisher gives no publisher match, but the pair stays in the denominator.

## How we get the expected recurrence

We use two random models: year, and year plus primary topic category.
Larger journals get more weight, based on their paper counts in each group.

1. Count each paper once to get the journal weights.
2. Keep each author's paper count, dates and topic categories. Assign a journal
   to each author-paper position and rebuild the publication history.
3. Count recurrence using the same rules as for the real data.
4. Repeat 100 times per model, with seed 42. Divide the observed rate by the mean
   simulated rate.

For Q1, about 0.1114 / 0.0361 gives 3.09 with the year model.

We draw with replacement: the same journal can come up again and its weight stays
unchanged. We are not modelling a fixed number of journal places. Co-authors can
receive different simulated journals because each author-paper pair gets its own draw.
This is our comparison model, not a claim that real authors choose independently.
Drawing without replacement would be a different model; we have not implemented it.

### What the intervals mean

The middle 95% of the 100 simulated rates shows variation within the random model.
It is not a confidence interval for the ratio.

For the ratio intervals, we resample whole authors 4,000 times and divide their
observed and expected totals. We calculate the expected totals directly under the
same random model, so the denominator has no simulation noise. The original
100-run results remain alongside these results.

These are nominal 95% intervals assuming independent authors and fixed journal
weights. We do not re-estimate the weights or publisher mapping in each sample.
Shared papers make authors dependent, which this bootstrap does not cover.
We have not established 95% coverage for the actual corpus.

## Where topics enter

Q1 and Q2 both use topic categories in the second random model. They do not use
Pierre's continuous historical topic value T. His Q1 Intra file describes similarity
among papers an author already published in one journal and is a separate result.

To adjust Q1/Q2 for historical T, we would need profiles for return opportunities
and alternative journals. The Q3 table stops after first entry, so it cannot supply
those return rows. Our current results do not establish topic-independent loyalty.

## Q3: what one row means

Each row is an author, a journal they have not entered before, and a year t.
There are 6,422,558 rows, including opportunities without entry. Without these,
we would have no denominator for the entry probability. We use opportunity set A;
set B is a separate variant.

- C records a prior connection. The same co-author must have both collaborated
  with the author and published in the target journal before t.
- F records first entry, using `entering_work_id`.
- T compares the author's and journal's profiles from years strictly before t.
  We can calculate this even when there is no entry paper.

Before combining B and C, the notebook checks that their author/journal/year keys
and row order match. We use the 1,106,356 rows with measurable T for adjusted models.
Missing T stays missing: zero would mean low fit, not unknown fit. These complete
cases are a selected population; excluding missing values does not remove selection bias.

## How we calculate Q3

1. Fit a logistic model with C and continuous T.
2. Predict each row once with C=1 and once with C=0, keeping T unchanged.
3. Average each set of probabilities and divide the two averages.

This is a standardized risk ratio. Taking the exponential of the C coefficient
would give an odds ratio instead.

We also fit an outcome for entries without a ride:
`first_entry * (1 - first_entry_ride)`. The qualifying earlier co-author must be
absent from the selected entry paper. Ride rows stay in the model with outcome zero;
removing them would select rows based on the entry itself. This distinction depends
on the seed history and does not isolate a direct network effect.

### Journal, year and prior paper count

We add journal and year as separate terms to check how much differences between
them matter. We check journals with zero entries for each outcome and exclude their
union from all compared models. Here that removes one journal and 17,936 rows.
The remaining journals and years must have events and non-events for both outcomes.
This exclusion depends on the outcomes.

On the same 1,088,420 rows, the non-ride ratio falls from 3.30 to 1.18 and the
all-entry ratio from 6.01 to 2.27. The C+T results using all complete cases are
3.34 and 6.09. We show both models because the difference matters to our conclusion.

Step 9 also adds `log1p(n_prior_papers)`, with and without journal and year.
This counts earlier corpus papers, not just papers used in the embeddings.
The log makes differences in count matter less at higher counts. With journal and
year, the ratios become 1.21 for non-ride and 2.29 for all entries; without them,
3.10 and 5.62. [D lists all estimates and intervals](../D_results/README.md).

Earlier paper counts and T may already reflect collaboration. Adding them does
not prove a causal effect or turn T into a measure of topic alone.

### Q3 intervals

We use the delta method with clustering by author, including the Step 9 models.
This allows repeated rows from one author, holds the included covariates fixed and
assumes independent author clusters. It replaces the earlier bootstrap plan.
Co-author and shared journal/paper dependence are not fully covered. An attempted
two-way covariance calculation did not give a valid covariance matrix.
The results remain associations, with uncertainty from model choice and missing T
outside these intervals.

## Rebuild the opportunity table

With the shared data configured, run from the repository root:

```sh
python3 project_data.py fetch --group logic
python3 B_opportunities_and_analysis/build_event_table.py
```

This writes both variants to B/data. Rebuild in a separate checkout so you keep
your downloaded inputs. The [schema](schemas/event_table.md) explains the columns
and eligibility rules; the [Python/Prolog report](event_table_parity.md) records
the row comparison.
