# Schema: Q3 event table

We are looking at first entry into a journal at the level of an active author,
a target journal, and a year. Each row is one opportunity, including years in
which the author does not enter the journal. These non-entry rows provide the
denominator for Q3.

The table uses years rather than exact dates:

- a row is `(author_id, journal_id, t)`;
- the author published somewhere in the corpus in year `t`;
- the author had not published in the target journal in a year before `t`;
- all history used for `C`, `T`, and prior-paper counts is strictly before `t`;
- the pair stops producing rows after its first entry year.

A common annual window is the implemented design, not the only possible one.
Two reasons led to it: OpenAlex fills a missing day and month with January 1,
and 28.6% of the corpus carries that date, so exact dates are unreliable for a
large share of papers even though not every January 1 is necessarily imputed;
and non-entry rows have no event date of their own, so a shared reference point
per year keeps the exposure window the same for entry and non-entry rows. Other
properly constructed time scales are possible but are not implemented.

## Columns

The delivered CSV (`event_table_topicmatch_v5.csv`, 6,422,558 rows) carries
these 15 columns in this order.

| Column | Type | Meaning |
|---|---|---|
| `author_id` | string | Short OpenAlex author ID (`A...`). |
| `journal_id` | string | Short OpenAlex source ID (`S...`) of the target journal. |
| `t` | integer year | Opportunity year. History means years strictly smaller than `t`. |
| `n_prior_papers` | integer | Number of the author's corpus papers in years before `t`. |
| `coauthor_seed` | 0/1 | `C`. At least one earlier collaborator also published in the target journal before `t`. Both conditions must hold for the same collaborator. |
| `t_first_seed` | nullable integer year | Earliest year in which the seed condition became true for the author-journal pair. |
| `first_entry_independent` | 0/1 | First entry in year `t` without a qualifying seed collaborator riding on the entering paper. This also includes entries with `C = 0`. |
| `first_entry_ride` | 0/1 | First entry in year `t` where the same collaborator who qualifies the seed is also on the entering paper. |
| `entering_work_id` | nullable string | Earliest work creating the entry in year `t`; empty on non-entry rows. |
| `publisher_id` | nullable string | Parent publisher of the target journal (`P...`). |
| `topic_match` | nullable float 0-1 | `T`. Rolling similarity between the author's pre-`t` topic profile and the journal's pre-`t` topic profile. Keep it continuous. |
| `n_profile_papers` | nullable integer | Number of usable author-profile papers strictly before `t`. Filled as 0 when the author has no paper before `t`; empty on the `below_threshold_no_abstract` rows, where the author has papers before `t` but none with a usable abstract. |
| `n_journal_papers` | integer | Number of usable journal-profile papers strictly before `t`. Depends only on `(journal_id, t)` and is the same for every row with that pair; 0 where the journal has no profile yet. |
| `profile_cutoff` | nullable integer year | Latest year included in the author profile. When `topic_match` is filled, this is smaller than `t`; empty when no author profile exists. |
| `tm_status` | string | Reason why `topic_match` is filled or missing. |

## Reading the entry flags

- `F = first_entry_independent OR first_entry_ride`.
- The split is an outcome split, not a row filter: whether a seeder ends up on
  the entering paper is itself a consequence of `C`, so filtering rows on such a
  flag would be post-treatment selection.
- Q3 is reported twice. Q3_all uses `F` as the outcome. Q3_ind uses
  `first_entry_independent` as the outcome. In both cases one logistic model
  `outcome ~ C + T` is fitted on the rows where `T` exists, every included row is
  predicted once with `C = 1` and once with `C = 0`, and the ratio of the two mean
  predictions is reported. Under `C = 0` no seeder exists, so every entry there is
  independent by definition, which is why the same model serves both predictions.
  The result is an association standardized over the included rows; reading it as
  a causal effect would need the usual assumptions, which are not established here.
- The two entry flags are mutually exclusive.
- A ride requires one matching collaborator across all three facts: earlier
  collaboration, earlier publication in the target journal, and presence on
  the entering paper. Combining separate Boolean seed and pathway flags is not
  sufficient because they may refer to different collaborators.
- `t_first_seed` belongs to the author-journal pair, not to a single row. It can
  therefore lie in year `t` or later on rows where `coauthor_seed = 0`. For
  predictive work it is only available when `t_first_seed < t`, exactly when
  `coauthor_seed = 1`.

## Topic-match status

`topic_match` is a continuous score. An empty value means unknown, never zero.
The v5 export has no whole-period paper threshold: whether `T` exists depends only
on history strictly before `t`. Journal profiles are built from every embeddable
paper in the corpus before `t`, not only from papers of authors with a profile.

Status values observed in the v5 export, with row counts:

- `ok` (1,106,356): author and journal profiles exist and `topic_match` was calculated;
- `no_author_history` (4,989,914): the author has no paper before `t`;
- `no_author_and_journal_history` (253,203): both profiles are missing;
- `below_threshold_no_abstract` (55,822): the author has papers before `t` but
  none with a usable abstract;
- `no_journal_history` (17,263): the author has a profile but the journal has no
  usable paper before `t`.

Other documented status labels, absent from this v5 export, include
`below_threshold_unproductive` from the superseded thresholded run and
`author_not_in_db` for an author absent from the topic-model input. The statistical
treatment of unknown `T` is kept separate from the schema.

The topic score is rolling: author and journal profiles use papers from years
before each row's `t`. A profile frozen at first seed can only be examined inside
seeded pairs unless a common anchor for `C = 0` is defined.

## Opportunity sets

- Variant A uses all 64 corpus journals that the author had not entered before
  year `t`. This is the main table.
- Variant B restricts the targets using the author's earlier primary topics and
  journals publishing those topics in year `t`. It falls back to A when the
  author has no earlier corpus paper. Because B uses publications from year `t`
  to form the set, it is kept as a sensitivity analysis rather than an ex-ante
  risk set.

## Scope and checks

- The observed corpus covers 64 journals and years 2015-2024. Publications and
  co-authorship outside this corpus are not visible, and an entry before 2015
  cannot be detected.
- Variant A contains 6,422,558 rows, 96,819 entries, 19,035 seeded rows,
  1,784 seeded entries, and 756 rides.
- The official topic input is Pierre's v5 export `event_table_topicmatch_v5.csv`
  (sha256 `8a9e8a9257f3f00ce39a71f0dcefd09cd10bc1d8200580426ee94346284b2e37`,
  497,765,187 bytes, delivered 2026-09-07). Audited: the ten event columns and
  keys match the Variant A table row for row, `tm_status == ok` exactly where
  `topic_match` is filled, `profile_cutoff < t` on every filled row, and an
  independent regeneration of the pipeline matches every status and count column
  with `topic_match` agreeing to 4.7e-7.
- An independent Prolog implementation matched all 6,422,558 Variant A
  opportunity keys and the `C`, `F`, and ride flags; review of those rules is a
  separate validation step.
