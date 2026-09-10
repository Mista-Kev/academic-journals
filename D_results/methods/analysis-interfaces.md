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

## Q1/Q2: what we count

- **Unit:** one author-paper pair. Co-authors can have different publication
  histories, so we evaluate each author separately.
- **History:** strictly earlier publication dates. Papers on the same date do
  not count as history for each other.
- **Denominator:** all 110,654 pairs, including first papers. This measures
  recurrence across the observed publishing activity.
- **Q1:** earlier publication in the same journal; 12,325 cases.
- **Q2 wide:** earlier publication with the same known parent publisher,
  including the same journal; 15,770 cases.
- **Q2 narrow:** earlier publication in another journal of that publisher;
  4,919 cases. Of these, 1,468 are also Q1 returns. The remaining 3,451 have
  no separate null comparison. Unknown publishers produce no publisher match;
  those pairs remain in the denominator.

## Q1/Q2: how we calculate the comparison

We use two reference models for both questions: **year** and **year plus primary
topic category**. Journal frequencies account for differences in journal size;
the second model also accounts for broad thematic concentration.

The notebook functions `build_dist` and `null_rates`:

1. Count each paper once to obtain journal weights within each year or year/topic group.
2. Keep each author's paper count, dates and categories. Assign journals to all
   author-paper positions, rebuilding the full journal history.
3. Apply the same recurrence rules to the simulated history.
4. Repeat 100 times per model, with seed 42. Calculate
   **observed rate / mean simulated rate**, not the mean of individual ratios.

For example, Q1's observed rate of about 0.1114 divided by the year-model expected
rate of about 0.0361 gives 3.09.

### Why sampling with replacement?

- We use fixed journal weights. A journal can be drawn repeatedly without changing
  the next draw's probabilities. This gives a reference for recurrence under
  independent assignments, without assuming a limited number of publication slots.
- This does not mean real authors choose independently. Journal totals vary between
  simulations, and co-authors of one paper can receive different simulated journals
  because the draws are per author-paper pair.
- A permutation without replacement could preserve journal totals and still allow
  recurrence if several slots carry the same journal. That is a different reference
  model and was not implemented.
- The 100 simulations estimate the expected rate. They do not provide confidence
  intervals for the observed ratios.

## Where topic information enters

- **Q1/Q2:** primary topic category enters the second reference model for both
  questions. Continuous historical topic fit T is not included.
- **Q3:** T compares the author's earlier research profile with the journal's
  earlier profile. It remains continuous; we do not introduce a match/no-match threshold.
- **Q1 Intra:** Pierre's `topic_match_intra` describes similarity among an author's
  papers already published in one journal. It is a separate descriptive output.
- **What is missing for T-adjusted Q1/Q2:** historical profiles for return
  opportunities and alternative journals. Q3 stops after first entry and cannot
  supply return rows. The current ratios and Intra do not establish topic-independent loyalty.

## Q3: what we count and why

- **Unit:** author, journal not previously entered, and year t. The 6,422,558 rows
  include opportunities without entry; otherwise we would have no comparison denominator.
  Opportunity set A is the main input; B is a separate table variant.
- **C, prior connection:** the same co-author must provide both earlier
  collaboration and earlier publication in the target journal. Combining evidence
  from two different people would create a connection neither person actually provides.
- **F, entry:** derived from `entering_work_id`.
- **T, topic fit:** profiles use papers from years strictly before t. Historical
  profiles can be measured even when there is no entry paper. The common yearly
  cutoff gives entries and non-entries the same information window.
- **Input check:** B and C must have identical author/journal/year keys and row
  order before their fields are combined.
- **Missing T:** we use the 1,106,356 complete cases. Zero would assert low fit
  when fit is unknown. Restricting the population avoids inventing values, but
  does not remove selection bias.

## Q3: how we calculate the result

1. Fit a logistic model with C and continuous T for the chosen outcome.
2. Predict each included row once with C=1 and once with C=0, keeping T unchanged.
3. Average the predicted probabilities for each setting and divide the two averages.
   This gives a standardized risk ratio. Exponentiating the C coefficient would
   instead give an odds ratio.

### Non-ride outcome

- We use `first_entry * (1 - first_entry_ride)` to distinguish entries without
  the qualifying seed co-author on the selected entry paper.
- Both predicted risks come from this outcome's model. Ride rows remain in the
  population with outcome zero; removing them would change the comparison population
  based on the entry itself.
- Non-ride does not identify a direct network effect. Its classification still
  depends on the seed history.

### Journal and year comparison

- We add separate journal and year terms to examine how much the result depends
  on differences between journals and years.
- One journal with no entries is excluded to handle separation, removing 17,936
  rows. This restriction depends on the outcome.
- On the same remaining 1,088,420 rows, non-ride changes **3.30 → 1.18** and all
  entries **6.01 → 2.27**. The full complete-case C+T results are 3.34 and 6.09.
  We show both specifications because this difference changes the interpretation.

### Uncertainty and limits

- Adjusted intervals use an **author-clustered delta method** to account for
  repeated rows from the same author. This differs from the earlier bootstrap plan.
- Author clustering does not fully cover shared journal/paper dependence. Attempted
  two-way covariance estimates were not positive semidefinite. No new v5 bootstrap
  refits or bootstrap likelihood-ratio test were run.
- Complete cases are selected, and pre-t topic profiles may already reflect
  earlier collaboration. The results are therefore reported as associations,
  not identified causal effects.

[Results and intervals](../README.md) · [Decision history](decisions.md)
