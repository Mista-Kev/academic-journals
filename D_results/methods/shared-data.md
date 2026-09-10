# Shared data: GitHub code, SharePoint files

The large research files belong in the team's **Applied AI Group B Data**
SharePoint folder. Code and `data-manifest.json` belong in GitHub. The manifest
records the exact path, size, SHA-256, owner and purpose of every selected file.
It contains no private access links or credentials.

## Folder layout and migration

The repository now uses A/B/C for the producing parts and D for the combined
interpretation. Each data artifact has one canonical path:

```text
  A_data_and_rules/data/openalex_ai_raw_v1_0.jsonl
  A_data_and_rules/data/openalex_ai_semiclean_v1_0.csv
  B_opportunities_and_analysis/data/event_table_python_v0_oppA.csv
  B_opportunities_and_analysis/data/event_table_python_v0_oppB.csv
  A_data_and_rules/data/event_table_prolog_v0_oppA.csv
  C_topic_match/data/event_table_topicmatch_v5.csv
  C_topic_match/data/event_table_topicmatch_local_min3.csv
  A_data_and_rules/results/openalex_three_path_v1_0/journal_parent_publishers.csv
  A_data_and_rules/results/openalex_three_path_v1_0/pathway_flags.csv
  A_data_and_rules/results/openalex_three_path_v1_0/pathway_evidence.csv
  A_data_and_rules/results/openalex_three_path_v1_0/pathway_results.csv
  C_topic_match/results/results_q1_topic_match_v5.csv
  B_opportunities_and_analysis/results/q3_v5/model_results.json
```

The current cloud delivery is the **official-v5-2026-09-07-abcd-v1** subfolder
inside **Applied AI Group B Data**. It contains the A/B/C layout above and four
root metadata files. The earlier `data/`, `results/` and `topics/Results/` layout
remains available in the parent shared folder. The manifest records those older
locations as `shared_path`. The loader first looks for
the new A/B/C path and otherwise uses that explicit old path. Either copy must
match the same size and SHA-256; a differing new-path file is rejected rather
than silently replaced by the old copy.

`prepare-release` writes the complete new A/B/C delivery, including instructions
and metadata; `stage` remains available for data-only or single-group staging.
The migration mapping is in
[layout-migration.json](layout-migration.json). This changes file locations,
not the frozen v5 data release or its checksums. Keep the old release readable
until the matching code has been published and collaborators have switched.

The historical Min-3 file remains necessary for Q3 step 8; it is not the main
input. The Q1 Intra export describes observed groups and does not adjust Q1/Q2.
The Q3 result JSON is **external reference evidence**, produced by `refit.py`
in the separate offline v5 demo package. That producer is not included in this
repository. The loader retrieves its frozen, hash-checked output; it does not
regenerate it. The Q3 notebook computes its own estimates and printed results;
the JSON additionally supplies reference delta intervals for the sensitivity fits.

## One-time setup for each person

Use Python 3.12 or newer. Each person needs permission to read the shared folder.
The code does not borrow another person's browser session or change permissions.

**Browser download (also works in the guest view):** open the team's shared
folder, then open **official-v5-2026-09-07-abcd-v1**. Select **Download** with no
individual file selected, and extract the ZIP. Do not download the parent folder,
which also contains the previous delivery. Keep the folder structure intact.
Configure `shared_root` as the extracted release root containing A/B/C and
`START_HERE.txt`, not an outer ZIP wrapper or the parent shared folder.
From the repository root, run these commands with your actual extracted path:

```sh
python3 project_data.py configure --shared-root "/path/to/official-v5-2026-09-07-abcd-v1"
python3 project_data.py fetch --group q3
```

`configure` verifies the files against the repository manifest before saving
their location in the ignored `.shared-data.local.json`. Use `--group q1-q2`
or `--group q3` on `configure` if you downloaded only that group's files.
Then fetch the same group, or open its notebook from `B_opportunities_and_analysis/`.
The loader copies and verifies the required inputs; no manual per-file placement
inside the repository is needed. This is a downloaded snapshot, not continuous
synchronization. For updates, download the newly agreed release and verify it
against the corresponding repository manifest.

**Synced folder:** synchronize the SharePoint folder with OneDrive and make its
files available locally. Run the same `configure --shared-root` command with
your own synced **official-v5-2026-09-07-abcd-v1** release folder, the directory
containing A/B/C and `START_HERE.txt`. The notebooks reuse that saved location.

Alternatively set the `ACADEMIC_JOURNALS_SHARED_ROOT` environment variable to that
folder. It overrides the local config. An explicit `fetch --shared-root` overrides
both for that invocation without changing the saved configuration. `configure`
refuses a conflicting environment override because its newly saved setting would
otherwise have no effect. Unset the variable before saving a different source.
There is no workstation path in the notebook itself.

**Direct downloads:** if the shared files have permitted HTTPS download links,
put them in the ignored local config, keyed by repository-relative file path:

```json
{
  "urls": {
    "C_topic_match/data/event_table_topicmatch_v5.csv": "DIRECT_HTTPS_FILE_DOWNLOAD_LINK"
  }
}
```

The loader also accepts legacy URL keys from the manifest's `shared_path` when
no new-path key exists. A new-path key always wins; a bad new link never silently
falls back to an old one.

That is a format example, not a working URL. A folder-view link or sign-in page
is not a CSV. This lightweight client does not implement Microsoft Graph login;
for links requiring interactive authentication use the synced/downloaded-folder
route. Expiring preauthenticated download URLs are not permanent project IDs.
Never commit signed links or credentials to the public repository.

## Run an analysis

From the repository root:

```sh
python3 project_data.py list --group q3
python3 project_data.py fetch --group q3
```

Or run Q1/Q2 or Q3 from `B_opportunities_and_analysis/`: their first code cell calls the same loader.
Notebook input paths now follow the A/B/C layout. The loader checks already present files,
fetches only missing files, and verifies both size and SHA-256 before exposing
them to the analysis. A second run can use the verified local files offline.
A differing local file causes an explicit error; it is not overwritten.

The tracked reference CSVs are marked `-text` in `.gitattributes` so Git preserves
their exact stored bytes, including when `core.autocrlf=true`. Checksums remain
strict. An older checkout may already contain converted copies: preserve any
intentional local edits before restoring the affected reference files from Git
or retrieving the verified shared copies. Do not change manifest hashes to accept
line-ending conversion. Fresh checkouts with these attributes need no repair.

Groups:

| Group | Use |
|---|---|
| `q1-q2` | Semiclean corpus, publisher mapping, pathway flags |
| `q3` | Annual Python table, official v5 T and historical Min-3 comparison |
| `logic` | Inputs needed by the annual Python builder, including pathway cross-check files |
| `parity` | Existing Python and Prolog annual outputs for comparison |
| `corpus` | Raw and semiclean frozen OpenAlex corpus |
| `topics` | Annual input to Pierre's notebook; **not** its complete DuckDB/GPU environment |
| `outputs` | Pathway evidence/results, Intra result and checked Q3 result JSON |
| `sensitivity` | Variant B table |
| `all` | All 13 declared artifacts, about 2.65 GB |

The raw→DuckDB preparation and SPECTER2 execution are not automated by this
loader. It changes data acquisition, not statistical definitions or the other
open notebook-review issues.

## Put checked outputs in SharePoint

Keep analyses writing their outputs locally. Publish a deliberate verified
snapshot, so rerunning a notebook cannot overwrite the team's reference files.
For the currently declared files:

```sh
python3 project_data.py verify --group all
python3 project_data.py prepare-release --target /path/to/dedicated-release-folder
python3 project_data.py verify-release --target /path/to/dedicated-release-folder
```

Use your actual path. The destination must be the directory that will contain
the A/B/C data folders. `prepare-release` copies only the 13 manifest-listed files
and writes four metadata files: `START_HERE.txt`, `FILES.md`, `data-manifest.json`
and a deterministic `delivery-*.json` receipt. Instructions name the repository
commands; the inventory identifies each file's purpose and producer. D remains
in GitHub because it contains the combined interpretation, not another data copy.

Use a dedicated empty folder outside the repository. Repeating preparation on
an identical release is safe. A differing existing data or metadata file, or
unexpected content such as private notes, causes an error before copying files.
Regular `.DS_Store`, `desktop.ini` and `Thumbs.db` files are tolerated because
Finder and Windows can create them while browsing. They are not release artifacts,
are not hash-checked and are never collected from the repository by the staging
command. Same-named directories or symlinks are still rejected.
Both `stage` and `prepare-release` reject destinations inside the repository or
containing it. `stage --group ...` writes its own group receipt. To prepare a
complete release afterwards, choose another empty folder; do not promote a
subset folder by deleting its receipt. Receipts and old releases are preserved.

Atomic file publication requires hard-link support and write permission in the
cache or staging destination. If the filesystem refuses this, the command fails
without publishing a partial file. Use a writable local APFS/NTFS directory and
upload the completed release through SharePoint. A synced source can still be
read into that local cache; direct staging onto every cloud or network filesystem
is not supported.

The command never recursively collects the source checkout. A failed or
interrupted preparation is not a completed delivery: `verify-release` must pass.
It checks all data **and metadata** against the matching repository version.
Changing the instructions in code or manifest wording (even a purpose description)
requires preparing new metadata in a new folder for the next published delivery;
the verifier intentionally refuses stale instructions. `stage --group q3` can
still prepare selected data, but that is not a complete release.

If the target is a OneDrive-synced folder, wait for synchronization and check the
files on SharePoint before claiming that the upload completed. Otherwise upload
the prepared directories through SharePoint's folder-upload control.

### Switch after review and code publication

1. Publish the reviewed code with the A–D paths and these release commands.
2. Upload the **contents** of the prepared release to a new, separately named
   SharePoint release folder, including all four root metadata files. Preserve
   the existing `data/`, `results/` and `topics/Results/` release while people switch.
3. Download the new release into a different local folder, extract it and run
   `verify-release --target "/path/to/downloaded-release"` from that code version.
   A successful local preparation does not prove the upload or readback succeeded.
4. Configure that downloaded or synced release root and run both demos. Ask a
   recipient to follow `START_HERE.txt` with their own account before declaring
   recipient access tested. Permissions and OneDrive setup are separate from hashes.

Preparation alone does not change `.shared-data.local.json`, notebook cells,
SharePoint contents or the team's current reference release. A fresh recipient
cache can be tested with `--root` pointing to a separate folder containing the
matching repository manifest. Verification itself requires no data copy.

For a future data release, assign a new release label and review the manifest's
explicit file list and hashes. Preserve the old release in a separately named
folder before publishing changed values. Do not silently replace the reference
file or update its hash merely to silence a verification failure.

## Validation and deployment status

The loader has local tests for verified source configuration, first retrieval and offline reuse, corrupted or
truncated transfers, existing-file preservation, staging conflicts, path escape,
login-page rejection and avoiding secret URLs in errors. On 9 September 2026, SharePoint confirmed upload completion for all 13
declared artifacts plus the manifest and entry-point instructions. All 13
artifacts were downloaded again and matched their exact byte sizes and SHA-256
hashes against the repository manifest. Root metadata files were observed in
SharePoint but were not separately hash-checked after download.

Both notebooks' first code cells passed in a fresh temporary repository/cache
using only those downloaded inputs: Q1/Q2 loaded 27,400 papers across 64 journals;
Q3 loaded 6,422,558 rows, 96,819 entries and 19,035 seeded rows. The same cache
then worked with the source configuration removed, proving offline reuse.
Those checks concern the original loader branch. The A–D migration and full-notebook reruns are recorded separately in [validation.md](validation.md).

The current local checkout is configured to use a persistent **downloaded
SharePoint snapshot**. It is not an automatically synchronized OneDrive folder.
OneDrive synchronization and access as Felix or another recipient have not been
independently tested. A different user configures their own downloaded or synced
folder using the command above.

The A–D code was merged in PR #63; the portability follow-up is `edc7641`.
On 10 September the A/B/C release was uploaded to the new subfolder. All 13 data
files and four metadata files were downloaded separately and matched their exact
sizes and SHA-256 hashes. Q1/Q2 and Q3 then ran on those downloaded inputs and
matched the prior full output logs. Because local disk space was limited, three
large files not required by those demos were discarded only after their downloaded
bytes had been verified. The retained analysis-input folder is therefore a partial
local copy, not a full release to redistribute. The cloud folder contains all 17
files. See [validation.md](validation.md) for the checks and their limits.

Microsoft documents [SharePoint/OneDrive synchronization](https://support.microsoft.com/en-US/sharepoint/sync/sync-sharepoint-and-teams-files-with-your-computer)
and [Graph file downloads](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0).
