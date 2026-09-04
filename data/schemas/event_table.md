# Schema: event table (draft for freeze)

One row per opportunity: an author a, a journal J that a has never published in before, at time t. Produced by the logic layer (Lennart's rules) joined with topic_match (Pierre). This is the single input for all of E4/E5.

| Column | Type | Meaning |
|---|---|---|
| author_id | string | OpenAlex author ID (A...) |
| journal_id | string | OpenAlex source ID (S...) of J |
| work_id | string | the paper creating the opportunity, for traceability |
| t | date | publication date of the opportunity paper; defines "strictly before t" everywhere (note: missing day/month defaults to Jan 1 in OpenAlex) |
| topic_match | float 0-1 | T: probability that the paper fits J topically (Pierre's classifier); thresholding happens downstream, keep the probability |
| coauthor_seed | bool | C: at least one co-author of a published in J strictly before t |
| first_entry_independent | bool | F_ind: first entry at t, and no seeding co-author is an author of the entering paper |
| first_entry_ride | bool | F_ride: first entry at t, and at least one seeding co-author is on the entering paper |
| subfield_id | string | stratum for the null models |
| year | int | stratum for the null models and for CPT stability checks |
| orcid_verified | bool | author has a verified ORCID; enables the ORCID-only robustness rerun |
| publisher_id | string | top element of J's host_organization_lineage (parent publisher, for Q2) |

Notes:

- F = first_entry_independent OR first_entry_ride, mutually exclusive. The joint-submission split is an **outcome split, not a row filter**: whether a seeder ends up on the entering paper is itself a consequence of C, so filtering rows on such a flag would be post-treatment selection.
- Q3 is reported twice: Q3_all uses F; Q3_ind uses P(F_ind | do(C on)) / P(F | do(C off)). Under do(C off) no seeder exists, so every entry there is independent by definition.
- Changes to this schema after the freeze need a team ping first.
