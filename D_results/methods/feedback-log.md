# Feedback log

Running log of external feedback and what we did with it. Newest first.

Template for entries:

```
## YYYY-MM-DD, <source>
Points: <numbered, one line each>
What changes: <concrete consequences>
What stays: <what remains valid>
```

## 2026-08-08, second-pass review of the adversarial fixes

Corrections to the first pass:
1. Mediator handling: the "two readings of T" choice becomes a time split: adjust for T_pre (pre-treatment topic profile), never condition on T_paper (mediator). The direct-effect reading carries two caveats: no unmeasured mediator-outcome confounding assumed, and "lower bound" is heuristic for a ratio metric (non-collapsibility).
2. The joint-submission split is an outcome split (F = F_independent + F_ride), not a row filter: filtering on a seed-on-paper flag would be post-treatment selection.
3. Clustering is wider than authors: journal-level and paper-level dependence too; plan two-way clustering (author x journal) or paper-level aggregation; the author-only bootstrap is the floor, not the ceiling.

New findings:
4. The opportunity set is itself a modeling decision: which journals count per (author, t); at least two definitions compared as sensitivity (decision issue).
5. Q2 must map publishers at publication time, not current lineage: OA M&A (e.g. Hindawi/Wiley) falls inside 2015-2024.
6. Q1 measures loyalty to surviving journals only: the frozen 64 exclude died or delisted journals (limitation).
7. Validation scope: the synthetic recovery test certifies the estimator, not the graph.

Actions: schema PR amended (outcome split), #50 extended (two-way clustering), new opportunity-set decision issue, S4.5 acceptance and S5.4 limitations updated, headline number pre-registered in decisions.md.

## 2026-08-08, adversarial self-review of the Q3 structure

Findings, one line each:
1. The timeline argument was backwards: C-events precede T, so C to T is admissible; T is then partly a mediator, and Q3 is the direct effect, a lower bound on total co-author influence.
2. Joint submissions: C and F can be one single event (first entry with the seeding co-author on the paper); Q3 conflates following with riding along.
3. Money is missing: institutional APC deals / transformative agreements drive journal preference and correlate with the co-author pool, bypassing topic.
4. Special issues / guest editors recruit whole networks into one journal: a common cause of C and F outside the model.
5. Rows are not iid (one paper spawns many rows, authors repeat): the textbook chi-square df 2 overstates significance.
6. Correlated author-ID error feeds both C and F: a node-shaped confounder; the ORCID-only rerun is its probe.
7. Smaller: pooling 2015 to 2024 in one CPT, lab/PI structure as the sharper shared-institution, author venue-trying heterogeneity as Q3's productivity margin.

What changes, cost-ordered: seed_on_entry column added to the event-table schema before freeze (Q3 reported twice: all vs independent entries); q3-structure.md reworked (timeline corrected, direct-effect interpretation, three new named threats, lag + year-stability diagnostics); author-level resampling replaces the naked chi-square in S5.2; T-measurement (entering paper vs pre-t history) opened as a decision issue.

What stays: the adjustment machinery, the do-queries, and the synthetic validation. Q3's meaning is sharpened to "direct, topic-unmediated effect", not discarded.

## 2026-08-04, week-2 check-in: supervisor feedback on the Q3 approach

Points:
1. Build the graph first: qualitative structure before any parameters.
2. The arrows are the real content, and the missing arrows even more so: every absent edge is a strong, contestable claim; challenging each one through logic is the work.
3. Order variables by time, left to right; arrows may only point forward in time.
4. State hypotheses from logic first, and test them early, before estimation.
5. Keep three activities distinct: causal structure specification (domain knowledge), structure learning (from data, limited by Markov equivalence), parameter learning (CPTs given a structure).

What changes: the structure derivation now precedes parameter work, see [q3-structure.md](q3-structure.md). The notebook is re-positioned as parameter learning, step 5 of 6, not step 1. H0/H1 are stated from logic before estimation.

What stays: the synthetic-data validation approach and the notebook itself remain valid, just later in the order.
