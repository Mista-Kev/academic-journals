# Research Notes (beyond the kickoff slides)

> **Historical document.** These were options and cautions collected before implementation. Some items were adopted, replaced, or found infeasible. They are not the current method specification.

The kickoff slides are the agreed baseline plan. These notes are *extra input* from prior research — pitfalls to avoid and optional upgrades. In the issues they are marked "(research)" or "(stretch)"; they never replace the baseline.

- **OpenAlex access (S1.2):** since Feb 2026 the API requires a free API key and is credit-metered (~100k credits/day free; list calls cost 10 credits). For bulk pulls prefer the free monthly snapshot or a one-time filtered pull; use pyalex; cache everything; key via `.env`.
- **Abstracts (S1.3):** delivered as an inverted index (word → positions) and must be reconstructed; 40–55% missing is normal for our slice — measure coverage early and decide title-only fallback vs. exclusion, documented.
- **Author identity (S1.6):** OpenAlex author IDs suffer over-lumping (several people merged → fake loyal super-authors) and over-splitting (one person scattered → loyalty destroyed), worst for common East-Asian names. Quantify on a small hand-checked sample, cross-validate against DBLP; feeds the ORCID-only rerun.
- **Temporal leakage (S2.2, S3.4):** the T0 < T guard is the defense — dedicated leakage review of every rule; journal topic profiles computed from *past papers only* (rolling window).
- **Q1 null model (S4.4):** the size-weighted redraw fixes only one margin and can overstate loyalty. Rigorous upgrade: degree-preserving bipartite configuration model fixing both margins (Curveball/fastball randomization, ~1,000 samples), stratified by subfield×year; empirical p with the +1 correction ((exceedances+1)/(N+1)) and a z-score.
- **Q2 publisher rollup (S4.5):** use OpenAlex `host_organization_lineage` to roll journals up to the parent publisher; validate against Crossref where lineage is missing; near-identical sister journals are close substitutes — interpretation caveat.
- **Survivorship bias (S5.4):** we observe publications, not submissions — measured loyalty is loyalty-conditional-on-acceptance (Wald's bombers); draft the limitations section early, not last.
- **topic_match stretch (S3.6):** SPECTER2 scientific-paper embeddings (citation-contrastively trained, 768-d, cosine to a past-only journal centroid) if word frequencies prove too coarse; keep the decision tree as the interpretable baseline and report both.
- **DeepProbLog limits (S7.3):** exact inference is weighted model counting, #P-hard — worlds explode combinatorially (2^n over probabilistic facts); stopping the PoC is a documented finding, not a failure.

## Baseline vs. upgrade

| Piece | Baseline (slides) | Research upgrade |
|---|---|---|
| Q1 null | size-weighted redraw of each author's journals | both-margins configuration model (Curveball), empirical p + z-score |
| Q2 reference | publisher market share in the field | `host_organization_lineage` rollup, Crossref-validated |
| Q3 | do-operator P1 ÷ P0 + nested-model test | leakage-reviewed events + past-only topic profiles (guardrails) |
| topic_match | decision tree on word features (Naïve Bayes comparison) | SPECTER2 embeddings (stretch) |
| Data access | OpenAlex API | free monthly snapshot / one-time filtered pull, cached |
