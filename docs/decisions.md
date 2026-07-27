# Decisions (ADR-light)

Template — 5 lines per decision:

```
## YYYY-MM: Title
**Context:** Why did this decision come up?
**Decision:** What was decided?
**Alternatives:** What was rejected, and why?
**Consequences:** What follows from it?
```

## 2026-07: Repo structure & tooling adopted as per slides v1
**Context:** Project start, shared working base needed.
**Decision:** Folder structure, roles, and toolchain (OpenAlex/DOAJ/ORCID → Prolog/Logtalk → topic_match → bn-logtalk → statistics) as per slides v1; repo language English; research notes adopted as extra input (pitfalls + optional upgrades, see `research-notes.md` — slides remain the baseline).
**Alternatives:** Monorepo without area folders; heavier tooling (CI, Docker) — rejected, entry barrier should be zero.
**Consequences:** One branch per area, PRs into `main`; CI/Docker/pre-commit possibly later.
