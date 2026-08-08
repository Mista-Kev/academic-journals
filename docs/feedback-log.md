# Feedback log

Running log of external feedback and what we did with it. Newest first.

Template for entries:

```
## YYYY-MM-DD, <source>
Points: <numbered, one line each>
What changes: <concrete consequences>
What stays: <what remains valid>
```

## 2026-08-04, week-2 check-in: supervisor feedback on the Q3 approach

Points:
1. Build the graph first: qualitative structure before any parameters.
2. The arrows are the real content, and the missing arrows even more so: every absent edge is a strong, contestable claim; challenging each one through logic is the work.
3. Order variables by time, left to right; arrows may only point forward in time.
4. State hypotheses from logic first, and test them early, before estimation.
5. Keep three activities distinct: causal structure specification (domain knowledge), structure learning (from data, limited by Markov equivalence), parameter learning (CPTs given a structure).

What changes: the structure derivation now precedes parameter work, see [q3-structure.md](q3-structure.md). The notebook is re-positioned as parameter learning, step 5 of 6, not step 1. H0/H1 are stated from logic before estimation.

What stays: the synthetic-data validation approach and the notebook itself remain valid, just later in the order.
