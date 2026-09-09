# A–D migration validation · 2026-09-09

Local integration branch: `structure/abcd-handoff`. Inputs: the verified downloaded
SharePoint snapshot, release `official-v5-2026-09-07`. Q3 code base: PR #60 head
`8d2810a`. Loader base: `b6462bb`. Schema source: local `40be940`.

| Check | Result |
|---|---|
| Shared source configuration and retrieval | All 13 artifacts verified against unchanged byte sizes and SHA-256; old remote paths read into new local paths |
| Full Q1/Q2 via `python demo.py q1-q2` | Passed, 35.5 s; year / year+topic ratios Q1 3.09 / 2.22, Q2 wide 2.02 / 1.69, Q2 narrow 1.16 / 1.11 |
| Full Q3 via `python demo.py q3` | Passed, 64.2 s; C+T 6.09 / 3.34; matched rows 6.01 / 3.30; journal+year 2.27 / 1.18 |
| Calculation-source comparison | All Q1/Q2 and Q3 code cells identical to the PR branch after removing the loader prefix and normalizing input paths |
| Python event builder | Both variants rebuilt twice, byte-identical on rerun; A 6,422,558 rows, B 5,763,341 |
| Prolog event builder | Passed fixtures and full build; 6,422,558 rows, 96,819 entries, 1,784 seeded entries, 756 rides; 37.1 s |
| Full row comparison | Zero missing keys, duplicate keys, C/F/ride disagreements; 52.7 s |
| Post-build manifest verification | All 13 artifacts still match, including both regenerated Python variants and Prolog output |
| Loader tests | 14 passed, including old-layout retrieval → new-layout staging → new-layout retrieval and rejection of conflicting versions |
| Rule tests | 12 passed including actual SWI-Prolog integration; TMPDIR=/private/tmp |
| Q3 failure checks | Complete separation, exhausted iteration budget and singular design rejected without returning an estimate |
| v5 schema | All 15 official column names documented |

The Python environment was the existing project virtual environment, not a new
package installation. The worktree started without large input files; the loader
populated them from the configured downloaded source. Notebook runs execute every
code cell and print fresh results without rewriting the notebook's stored outputs.
Timings are machine-dependent and some checks ran concurrently.

This validates local path migration and the analysis/demo route. It does not
validate access as another recipient, automatic OneDrive synchronization, the C
GPU/DuckDB reconstruction, or a causal interpretation. The new remote A/B/C folder
layout has not been published or moved; the compatibility mapping keeps the
existing cloud release usable. No branch was pushed as part of this migration.

## Review follow-up · 9 September

Both notebooks were executed again in fresh Jupyter kernels using the project
virtual environment, and their outputs are now saved in the notebook files:
Q1/Q2, eight code cells, 31.5 s; Q3, nine code cells, 54.5 s. The kernel runner
verified that execution did not modify cell sources and validated notebook format.

The calculation syntax trees are unchanged after accounting for two corrected
strings: the singular-design diagnostic and the false pre-2021 single-digit
caution. All Q3 printed results match the previous executed version after removing
loader status messages and normalizing that caution. The 14 loader and 12 rule
tests pass, all Markdown file links resolve, and all 13 manifest file identities
(path, bytes, SHA-256) are unchanged.

The decision record now distinguishes Kevin’s fixed local reporting position
from proposed adoption in the joint team report. Current notebook text refers to
the documented August comparison without asserting verified preregistration.
The frozen model-results JSON is explicitly external reference evidence, with its
producer outside this repository. Project documentation contains no agent attribution.

## Local SharePoint release preparation · 9 September

The complete A/B/C delivery was prepared locally from the unchanged frozen files:
13 data artifacts (2,648,058,868 bytes), plus `START_HERE.txt`, `FILES.md`, the
manifest and a delivery receipt. `verify-release` checked every data and metadata
file against the repository definition. No remote folder was changed.

The loader suite now has **18 passing tests**, including complete release → fresh
recipient cache, repeat preparation, metadata conflicts before data copying,
unexpected private content, and missing/corrupt metadata. Existing loading tests
continue to pass. Notebook cells, saved outputs and manifest hashes are unchanged.

A separate temporary code folder started with **none of the manifest data files**.
It verified and configured the prepared A/B/C release, then ran both complete demos:
Q1/Q2 in 29.0 s and Q3 in 56.2 s, using the existing project Python environment.
Q1/Q2 printed 3.09 / 2.22, 2.02 / 1.69 and 1.16 / 1.11; Q3 printed 6.09 / 3.34
and journal/year sensitivities 2.27 / 1.18. Output comparisons matched the earlier
logs after excluding loader/timing messages and the previously corrected year caution.
With the source configuration removed, both data groups passed again from cache.
The temporary recipient folder was removed after the check.

The local release uses independent APFS copy-on-write copies to conserve disk
space; no source file is hardlinked or symlinked into it. Ordinary release
preparation works by copying files and does not require APFS. Actual remote
upload/readback, recipient-account access and automatic OneDrive synchronization
remain separate checks after publication; this preparation does not claim them.

### Release review follow-up

The local integration now includes main's #60 merge (`0921ea0`); that merge
changed no files in the integrated tree. The loader suite has **20 passing tests**.
Regular `.DS_Store`, `desktop.ini` and `Thumbs.db` files are tolerated at the
release root and inside data directories. Symlinks and directories with those
names remain rejected, along with other unexpected content.

The unpublished local instructions now keep the disk-space estimate on one line;
the inventory explicitly labels its original manifest purpose text as English.
All 13 data files and four refreshed metadata files pass `verify-release`.
Metadata remains byte-exact by design; published metadata changes require a new
delivery folder and the corresponding repository version.

The private validation helper now normalizes only loader/timing messages and the
exact known historical caution. It raises on any remaining comparison mismatch.
Both saved notebook log pairs pass this stricter comparison. Deliberately altered
seed totals, seed coverage, warnings and caution text each raise an error.
No full notebook runs were repeated for this follow-up. Notebook files, data
hashes and statistical decisions remain unchanged. Nothing was pushed or uploaded.
