# topics/ — topic_match

**Purpose:** the topic-fit control T. Papers are embedded with SPECTER2 (title plus abstract), author and journal profiles are rolling centroids over papers from years strictly before t, and `topic_match` is the RBF-kernel similarity between the two profiles, a continuous value in (0, 1]. Empty is never zero: `tm_status` names the reason per cell. Kept continuous, no discretization; the whole-period eligibility threshold of the early runs is slated for removal, the threshold-free rerun is awaiting approval.
**Owner:** Pierre
**Input:** titles/abstracts from the raw OpenAlex data, event table rows from `logic/`
**Output:** `topic_match` plus diagnostic columns per (author, journal, t)
