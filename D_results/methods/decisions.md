# Decisions (ADR-light)

This file records decisions at the time they were made. Method details that remain under review are not settled merely because they appear in an earlier planning document.

## 2026-09-09: Reporting freeze for Kevin’s completed analysis

**Status and authority:** Kevin requested that the remaining choices be resolved
so his part can be completed and defended. The configuration below is the local
reporting decision applied in this integration. It does not claim prior approval
by Felix or the other team members, and is not a new preregistration. External
publication remains separate. Earlier plans below retain their historical wording.

**Q1/Q2 scope:** Finish the implemented observed/expected recurrence comparisons
using year and year plus primary-topic nulls. Pierre’s Intra summary is a separate
descriptive result. Historical continuous-T adjustment of returns is outside this
completed analysis; no claim of topic-independent loyalty is made. The existing
ratios answer explicit descriptive questions. A stronger question would require
return opportunities, historical profiles and alternatives, not a quick join or
an invented justification for the original omission. Q2 narrow’s overlap with Q1
is disclosed; no standalone publisher-only effect or null effect is established.

**Q3 population and missing T:** Fit and report the existing complete-case models
on the 1,106,356 opportunities where rolling historical T can be calculated.
Missing T stays unknown, not zero. Coverage and missingness reasons accompany the
results; descriptive full-table results remain separately labelled. No imputation,
weighting or missing-T indicator is added for this release. Extending to all
opportunities would require additional assumptions about histories and missingness
that have not been established. Restricting the target population is an explicit
scope choice, not evidence that selection bias or within-population confounding
has been eliminated.

**Q3 outcome and specifications:** Q3_ind, the non-ride outcome, remains the primary
outcome. C+T remains the originally planned primary comparison, reported as 3.34
[3.12, 3.58], together with the mandatory journal/year sensitivity of 1.18. For the
same 1,088,420 sensitivity rows the C+T comparison is 3.30 → 1.18. Q3_all is
secondary: 6.09 [5.76, 6.45], with matched-population 6.01 → 2.27. The sensitivity
excludes a zero-entry journal with 17,936 rows; this is outcome-conditioned.
Separate additive journal and year terms are used, not their interaction.

Keeping the original comparison preserves the question’s documented lineage;
it does not establish that its adjustment set is adequate. Making the richer
model primary would also need justification and a disclosed post hoc change.
The overall conclusion is based on both models: the association is strongly
specification-dependent and much smaller with journal/year controls. Neither the
large ratio alone nor a claim that 1.18 proves no relationship is an acceptable
summary. Primary-comparison status is not permission to hide the sensitivity.

**Uncertainty and causal interpretation:** Report the author-clustered delta-method
intervals actually calculated for the adjusted models, and the author-bootstrap
intervals where actually used for crude contrasts. This deviates from the original
adjusted-bootstrap plan; no new v5 bootstrap or confirmatory test is claimed.
The output is a model-based association, not an identified causal effect. Rolling
T may follow earlier collaboration. Non-ride does not mean network-independent.

**Fixed implementation:** Official v5 input; annual risk set A; B is a sensitivity;
strictly pre-t annual history; continuous rolling T; same-witness seed/ride logic;
logistic regression followed by standardization. A common annual window supports
a consistent definition for events and non-events. Properly aligned daily designs
are possible but not implemented. Frozen-profile checks inside C=1 are limited
by the lack of a common anchor for C=0 and do not become a required new analysis.

**Deliverable:** Runnable event construction and checks, Q1/Q2 and Q3 notebooks,
their results and a reasoning/demo guide. The earlier full BN/Logtalk software
plan is not claimed as implemented. The reasoning graph expresses assumptions;
it is distinct from the regression and the Prolog rule engine. Acceptance against
course requirements cannot be guaranteed by this local completion decision.

**Completion rule:** No additional model search or historical-T return analysis
is required to complete this explicitly bounded part. A failed validation or a
new substantive error can reopen a choice; a known, disclosed limitation alone
does not leave the analysis permanently provisional. Repo publication, shared-folder
migration, guide revision and rehearsal are remaining delivery tasks, not unresolved
statistical specifications.

Template — 5 lines per decision:

```
## YYYY-MM: Title
**Context:** Why did this decision come up?
**Decision:** What was decided?
**Alternatives:** What was rejected, and why?
**Consequences:** What follows from it?
```

## 2026-08-08: Headline number pre-registered
**Decision:** The headline result is Q3_ind: outcome split on independent entries, adjusted for T_pre, significance via author-level cluster-bootstrap CI. Every other variant (Q3_all, T_paper adjustments, alternative clusterings) is reported as robustness.

## 2026-07: Repo structure & tooling adopted as per slides v1
**Context:** Project start, shared working base needed.
**Decision:** Folder structure, roles, and toolchain (OpenAlex/DOAJ/ORCID → Prolog/Logtalk → topic_match → bn-logtalk → statistics) as per slides v1; repo language English; research notes adopted as extra input (pitfalls + optional upgrades, see `research-notes.md` — slides remain the baseline).
**Alternatives:** Monorepo without area folders; heavier tooling (CI, Docker) — rejected, entry barrier should be zero.
**Consequences:** One branch per area, PRs into `main`; CI/Docker/pre-commit possibly later.
