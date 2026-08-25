# Schema: Q3 event table

We are looking at first entry into a journal at the level of an active author,
a target journal, and a year. Each row is one opportunity, including years in
which the author does not enter the journal. These non-entry rows provide the
denominator for Q3.

The current table uses years rather than exact dates:

- a row is `(author_id, journal_id, t)`;
- the author published somewhere in the corpus in year `t`;
- the author had not published in the target journal in a year before `t`;
- all history used for `C`, `T`, and prior-paper counts is strictly before `t`;
- the pair stops producing rows after its first entry year.

Years rather than dates is deliberate: OpenAlex fills missing day and month with
January 1 (28.6% of the corpus), and non-entry rows have no event date of their
own, so only a common year-level reference point keeps the exposure window
independent of the outcome.

## Columns

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
| `n_profile_papers` | integer | Number of usable author-profile papers strictly before `t`. This count should be populated independently of whether `topic_match` can be calculated. |
| `n_journal_papers` | integer | Number of usable journal-profile papers strictly before `t`. This depends only on `(journal_id, t)` and should be the same for every row with that pair. |
| `profile_cutoff` | nullable integer year | Latest year included in the author profile. When `topic_match` is filled, this must be smaller than `t`. |
| `tm_status` | string | Reason why `topic_match` is filled or missing. |

## Reading the entry flags

- `F = first_entry_independent OR first_entry_ride`.
- The split is an outcome split, not a row filter: whether a seeder ends up on
  the entering paper is itself a consequence of `C`, so filtering rows on such a
  flag would be post-treatment selection.
- Q3 is reported twice: Q3_all uses `F`; Q3_ind uses
  `P(F_ind | do(C on)) / P(F | do(C off))`. Under `do(C off)` no seeder exists,
  so every entry there is independent by definition.
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
The current diagnostic export uses these status values:

- `ok`: author and journal profiles exist and `topic_match` was calculated;
- `no_author_history`: no usable author-profile paper exists before `t`;
- `no_journal_history`: no usable journal-profile paper exists before `t`;
- `no_author_and_journal_history`: both profiles are missing;
- `below_threshold_unproductive`: the diagnostic run excluded the author using
  the old whole-period paper threshold;
- `below_threshold_no_abstract`: the author did not reach the old threshold
  among papers with usable abstracts;
- `author_not_in_db`: the author was not found in the topic-model input.

The whole-period three-paper threshold belongs to the diagnostic run and is not
part of the intended Q3 input because it makes availability depend on future
productivity. The threshold-free export should also write the real profile and
journal counts on rows where `topic_match` remains missing. The statistical
treatment of unknown `T` is kept separate from the schema.

The current topic score is rolling: author and journal profiles use papers from
years before each row's `t`. A profile frozen at first seed can only be examined
inside seeded pairs unless a common anchor for `C = 0` is defined.

## Opportunity sets

- Variant A uses all 64 corpus journals that the author had not entered before
  year `t`. This is the current main table.
- Variant B restricts the targets using the author's earlier primary topics and
  journals publishing those topics in year `t`. It falls back to A when the
  author has no earlier corpus paper. Because B uses publications from year `t`
  to form the set, it is kept as a sensitivity analysis rather than an ex-ante
  risk set.

## Scope and current checks

- The observed corpus covers 64 journals and years 2015-2024. Publications and
  co-authorship outside this corpus are not visible, and an entry before 2015
  cannot be detected.
- Variant A currently contains 6,422,558 rows, 96,819 entries, 19,035 seeded
  rows, 1,784 seeded entries, and 756 rides.
- Pierre's diagnostic export matches the original Variant A event columns row
  for row. The final topic input still needs the threshold-free rerun.
- The Python event table is available for the Q3 analysis. Parity with the new
  Prolog event table is still pending.

## Opportunity set

Variant A (all 64 journals minus the already-entered ones) is the main table.
Variant B (journals publishing one of the author's earlier topics in year `t`)
is a sensitivity variant, not an ex-ante risk set, since it selects journals on
year-`t` publications.
