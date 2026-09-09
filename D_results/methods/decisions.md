# Decisions (ADR-light)

This file records decisions at the time they were made. Method details that remain under review are not settled merely because they appear in an earlier planning document.

## 2026-09-09: Kevin’s reporting position; proposed for the joint report

**Status:** Fixed working and presentation position for Kevin’s part. Adoption in
the joint team report remains proposed; no team or supervisor approval is claimed.
This is a present reporting decision, not a new preregistration. It closes the
scope of the local analysis without certifying causal validity or course acceptance.

**Context:** The August entry documents Q3_ind with T as the headline comparison.
On identical 1,088,420 measurable-T rows, adding separate journal and year terms
changes Q3_ind from 3.30 to 1.18 and Q3_all from 6.01 to 2.27. Those fits exclude
17,936 rows from a zero-entry journal, an outcome-conditioned restriction.

**Decision:** Complete Q1/Q2 as descriptive year and year+primary-topic reference
comparisons, with their overlap and historical continuous-T gap stated. For Q3,
use annual opportunity set A, continuous rolling pre-t T and the same-witness
seed/ride rules. Complete cases are the explicit adjusted-analysis population;
missing T is neither zero-coded nor imputed. Q3_ind remains the primary outcome;
C+T on all 1,106,356 measurable-T rows gives 3.34 [3.12, 3.58], reported together
with 1.18 from the journal/year sensitivity and its matched-row baseline 3.30.
Q3_all is secondary: 6.09 [5.76, 6.45] alongside 2.27 and matched baseline 6.01.
The conclusion is specification-sensitive association, not identified causation.

**Alternatives and reasons:** Keeping the August comparison preserves transparent
reporting history; it does not establish an adequate adjustment set. Making the
journal/year model primary is a defensible alternative only with its assumptions,
exclusion and post hoc change disclosed. Complete-case reporting avoids inventing
values for unavailable profiles but does not remove selection or confounding.
Generalization to all opportunities would require additional assumptions. A new
historical-T return analysis, a properly aligned daily design, a richer model or
imputation would answer additional questions and is not part of this bounded
completion. Frozen-profile checks within C=1 lack a comparable anchor for C=0.

**Consequences:** Show both Q3 specifications together and name their populations.
Report author-clustered delta intervals for adjusted models and bootstrap intervals
only where computed; the adjusted method differs from the August bootstrap plan.
Deliver regression with standardization, not an unimplemented full BN/Logtalk
system. Preserve association-only language, the non-ride definition and limits of
rolling T. No additional analysis is required by this local scope; substantive
errors can reopen it. Team adoption and publication remain separate handover steps.

Template — 5 lines per decision:

```
## YYYY-MM: Title
**Context:** Why did this decision come up?
**Decision:** What was decided?
**Alternatives:** What was rejected, and why?
**Consequences:** What follows from it?
```

## 2026-08: Q3 runs on the annual event table as implemented
Retrospective implementation record, updated after the September v5 delivery.
Current reporting status is defined by the September entry above.

**Context:** The event table and topic pipeline are implemented. Several details differ from the July plan.
**Decision:** Q3 uses one row per (author, journal, year) opportunity at year level; opportunity set A is the main table and B a sensitivity; T stays continuous with `tm_status` naming the reason for every missing value.
**Alternatives:** Day-level rows (a properly aligned daily design is possible; it was not built because non-entry rows have no event date of their own and 28.6% of corpus dates are January 1, so a common annual window was the simpler consistent choice); discretized T (arbitrary threshold, information loss).
**Consequences:** Q3 is estimated with logistic regression and g-computation rather than the planned bn-logtalk chain. The whole-period eligibility threshold in the topic pipeline was removed in Pierre's v5 export (delivered 2026-09-07, sha256 8a9e8a92), which an independent local regeneration matches on every status and count column, with topic values agreeing to within 4.7e-7. The embedding model's adapter configuration was compared and showed no meaningful effect (2026-09-03), so it is documented as a robustness check.
**Working positions at the time:** rolling author profile as the main T with the frozen profile only as a side check inside C = 1; complete-case fitting as the current treatment of missing T. Both are carried into the 2026-09-09 entry above as the fixed position for Kevin's part, proposed for the joint report.

## 2026-08-08: Historical entry — “Headline number pre-registered”
**Decision:** The headline result is Q3_ind: outcome split on independent entries, adjusted for T_pre, significance via author-level cluster-bootstrap CI. Every other variant (Q3_all, T_paper adjustments, alternative clusterings) is reported as robustness.

The historical title above is retained as written; it is not independent evidence
that all current specifications were preregistered. The present calculation uses
rolling T and delta intervals as disclosed in the September entry.

## 2026-07: Repo structure & tooling adopted as per slides v1
**Context:** Project start, shared working base needed.
**Decision:** Folder structure, roles, and toolchain (OpenAlex/DOAJ/ORCID → Prolog/Logtalk → topic_match → bn-logtalk → statistics) as per slides v1; repo language English; research notes adopted as extra input (pitfalls + optional upgrades, see `research-notes.md` — slides remain the baseline).
**Alternatives:** Monorepo without area folders; heavier tooling (CI, Docker) — rejected, entry barrier should be zero.
**Consequences:** One branch per area, PRs into `main`; CI/Docker/pre-commit possibly later.
