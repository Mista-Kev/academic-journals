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

The current cloud release still has its existing `data/`, `results/` and
`topics/Results/` layout. It has **not** been moved remotely by this local change.
The manifest records that location as `shared_path`. The loader first looks for
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
folder, select **Download** with no individual file selected, and extract the
ZIP. Keep the folder structure intact. Configure `shared_root` as the extracted
release root containing either the existing folders or the A/B/C folders.
From the repository root, run these commands with your actual extracted path:

```sh
python3 project_data.py configure --shared-root "/path/to/Applied AI Group B Data"
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
your own synced **Applied AI Group B Data** folder, the directory containing
the release folders. The notebooks reuse that saved location.

Alternatively set the `ACADEMIC_JOURNALS_SHARED_ROOT` environment variable to that
folder. It overrides the local config. There is no workstation path in the
notebook itself.

**Direct downloads:** if the shared files have permitted HTTPS download links,
put them in the ignored local config, keyed by repository-relative file path:

```json
{
  "urls": {
    "C_topic_match/data/event_table_topicmatch_v5.csv": "DIRECT_HTTPS_FILE_DOWNLOAD_LINK"
  }
}
```

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
The command never recursively collects the source checkout. A failed or
interrupted preparation is not a completed delivery: `verify-release` must pass.
It checks all data **and metadata** against the matching repository version.
Changing the instructions in code requires preparing new metadata in a new folder;
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
The branch and its notebook loader edits are local until explicitly published.

Microsoft documents [SharePoint/OneDrive synchronization](https://support.microsoft.com/en-US/sharepoint/sync/sync-sharepoint-and-teams-files-with-your-computer)
and [Graph file downloads](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0).
