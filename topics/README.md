# topics/ — topic_match

**Purpose:** the topic-fit control T. The current implementation embeds paper titles and abstracts with the SPECTER2 pipeline, builds rolling author and journal profiles from years strictly before `t`, and computes `topic_match` as a continuous RBF-kernel similarity. Empty is never zero: `tm_status` records why a value is unavailable. Removal of the earlier whole-period eligibility threshold and the model-adapter configuration are still under review.
**Owner:** Pierre
**Input:** titles/abstracts from the raw OpenAlex data, event table rows from `logic/`
**Output:** `topic_match` plus diagnostic columns per (author, journal, t)
