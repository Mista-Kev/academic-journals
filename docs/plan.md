# Project plan

> **Historical document.** This was the pre-kickoff scaffold. Several methods, ownership notes, and data assumptions changed during implementation. It is retained to show the original plan, not as the current specification. Use the implemented code, current schemas, reviewed notebooks, and recorded group decisions for the current state.

*Last updated 27 July 2026, before the kickoff. Decisions marked "pending" get filled in from the kickoff and mirrored into `decisions.md`.*

## What we are measuring

Why does a paper end up in one particular paid open-access journal? Three competing explanations, each expressed as **one number of the form observed ÷ expected**, where **1.0 = chance level** and **greater than 1 = genuine attachment**.

| | Question | Metric | Expected value comes from |
|---|---|---|---|
| **Q1** | Do authors return to the same journal? | repeat ratio | redraw each author's journals at random, weighted by journal size (stricter variant: also hold author productivity fixed) |
| **Q2** | Do they stay with the same publisher? | excess over market share | the publisher's market share in the field |
| **Q3** | Do they follow their co-authors? | P1 ÷ P0, topic-adjusted | an intervention on a small Bayes net, holding topic constant |

Scope: open-access journals charging APCs in AI / computer science, 2015–2024. We need the **full publication history** of the authors involved, not only papers in the target journals.

## Method spine

```
free data  ->  event table  ->  topic_match  ->  Bayes nets  ->  three numbers
(OpenAlex,     (Prolog rules,   (text model,     (CPTs, do-      (+ chance
 DOAJ, ORCID)   parity-checked)  soft labels)     operator)       baselines,
                                                                  significance)
```

Why the detour through an intervention for Q3: a co-author and a new journal often simply share a topic. Topic drives both sides, so it has to be held constant before anything counts as co-author influence.

## Who does what, in order

| # | Phase | Task | Owner | Needs | Blocks |
|---|---|---|---|---|---|
| 0a | now | Agree event-table schema (columns, types) | Kevin + Lennart | – | 1a, 3a, all probability work |
| 0b | kickoff | Record answers to the four open decisions | all | – | 1a, 2b, E7 |
| 1a | M1 | Fix scope: field filter, period, DOAJ/APC flag | Lennart | 0b (scope) | 1b |
| 1b | M1 | OpenAlex access + size estimate (snapshot, not the metered API) | Lennart | 1a | 1c |
| 1c | M1 | Pull works/authors/sources, join DOAJ/ORCID, reconstruct abstracts | Lennart | 1b | 2a, 3a |
| 1d | M1 | Data-quality memo: abstract coverage, ORCID coverage, disambiguation spot-check | Lennart | 1c | – |
| 2a | M2–M3 | Text features, decision tree, honest evaluation (CV + confusion matrix) | Pierre | 1c | 2b |
| 2b | M3 | topic_match per (author, journal, t), soft labels for EM | Pierre | 2a, 0b (DL level) | 4c |
| 3a | M2 | Fact export + Prolog event rules (`first_entry`, `coauthor_seed`, time guard) | Lennart | 0a, 1c | 3b |
| 3b | M2 | Parity check: Prolog against an independent Python count | Lennart | 3a | 4c |
| 4a | **from day 1** | Synthetic pipeline + parameter-recovery test (planted effect **and** planted null) | Kevin | 0a only | – |
| 4b | **from day 1** | Null-model machinery on toy data (Q1 both variants, Q2 benchmark), nested-model test | Kevin | – | – |
| 4c | M4 | Run everything on the real event table: CPTs, do-query, Q1 / Q2 / Q3 | Kevin | 3b + 2b | 4d, 5 |
| 4d | M4 | Robustness: ORCID-only rerun, VE vs. message passing, label-noise sensitivity | Kevin | 4c | 5 |
| 5 | M5 | Report, figures, defense — each writes their own methods section as they go | all | – | – |

### Three tracks run in parallel

| Track | Owner | Starts | Independent of |
|---|---|---|---|
| Data → events | Lennart | week 1, sequential | – (everything else waits on it) |
| Text → topic_match | Pierre | once abstracts exist (1c) | the logic track |
| Probability machinery | Kevin | **immediately**, on synthetic data | both other tracks until 4c |

**Critical path:** data pull → event table → the three numbers. Two notes on it. Kevin is the only one who can start today, since 4a and 4b need nothing but the agreed schema — and he is also the last to receive real inputs, so if 4a/4b are not finished early, M4 becomes a crunch. And 2b and 3b converge at 4c: if either slips, all three numbers slip, which is why both are checked against something independent before hand-over.

## Milestones

| | | Done when |
|---|---|---|
| **M1** | Scope and access | dataset size known, access confirmed, target group fixed |
| **M2** | Event table | Prolog events derived and matching the independent count exactly |
| **M3** | topic_match | text model trained and honestly evaluated (CV, confusion matrix) |
| **M4** | The three numbers | CPTs estimated, Q1/Q2/Q3 computed with chance baselines and significance |
| **M5** | Report and defense | result tables, figures, limitations, rehearsal |

## Open decisions (pending kickoff)

| | Question | Blocks | Answer |
|---|---|---|---|
| S0.1 | Deep-learning level: (a) pretrained embeddings as-is, (b) small classifier trained on top, (c) network inside the logic rules | S3.6, E7 | *pending* |
| S0.2 | Q1 chance model: size-weighted redraw, or hold author productivity fixed as well | S4.4 | *pending* |
| S0.3 | Scope: journals only, or do CS conferences count as venues | S1.1, dataset size | *pending* |
| S0.4 | Depth vs. breadth: three metrics thoroughly, or more questions | shape of E5 | *pending* |

Also open on our side: who leads the data pull, and whether we run the ProbLog / DeepProbLog proof of concept (E7) — Lennart's logic territory borders Kevin's probability layer, so ownership is settled at the kickoff. It runs parallel to the event rules, never instead of them.

## How we work

- **Asynchronous** through issues rather than fixed meetings. Decisions get written down in `decisions.md` so they survive.
- **Everything cross-checked**: Prolog against a Python count, the Bayes-net library against an independent implementation, results against a chance baseline.
- **Reproducible**: pinned requirements, fixed random seeds, free data only. Every number traceable back to the raw pull.
- **Write as you go**: each role drafts its own methods section during the work, not in the last week.

## Related documents

| File | Contents |
|---|---|
| `research-notes.md` | OpenAlex access and data quality, null-model background, known pitfalls |
| `decisions.md` | Decision log, including the kickoff answers above |
| repo issues | Epics E0–E7 with the individual stories and owners |
