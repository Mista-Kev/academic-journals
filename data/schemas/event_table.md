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
| seed_on_entry | bool | at least one seeding co-author is an author of the entering paper itself |
| first_entry | bool | F: a publishes in J for the first time at t |
| subfield_id | string | stratum for the null models |
| year | int | stratum for the null models and for CPT stability checks |
| orcid_verified | bool | author has a verified ORCID; enables the ORCID-only robustness rerun |
| publisher_id | string | top element of J's host_organization_lineage (parent publisher, for Q2) |

Notes:

- Q3 will be reported twice: on all entries, and on independent entries only (seed_on_entry = false). The gap between the two numbers separates "following a co-author" from "entering via a joint paper".
- Changes to this schema after the freeze need a team ping first.
