# logic/ — event layer

**Purpose:** Prolog/Logtalk rules derive events (`first_entry/3` via negation-as-failure, `coauthor_seeded/3` via reachability with a time bound) and export the event table ⟨target?, C, E⟩ per opportunity. An independent Python counting path serves as a parity check — it must match exactly on the sample.
**Owner:** Lennart (PoC part: Kevin)
**Input:** facts from `data/` (published/3, coauthor/2, publisher/2)
**Output:** event table in `data/`
