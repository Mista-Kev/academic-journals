# Shared data: GitHub code, SharePoint files

The large research files belong in the team's **Applied AI Group B Data**
SharePoint folder. Code and `data-manifest.json` belong in GitHub. The manifest
records the exact path, size, SHA-256, owner and purpose of every selected file.
It contains no private access links or credentials.

## Folder layout

The paths inside SharePoint match the paths relative to the repository root:

```text
Applied AI Group B Data/
  START_HERE.txt
  data-manifest.json
  data/
    openalex_ai_raw_v1_0.jsonl
    openalex_ai_semiclean_v1_0.csv
    event_table_python_v0_oppA.csv
    event_table_python_v0_oppB.csv
    event_table_prolog_v0_oppA.csv
    event_table_topicmatch_v5.csv
    event_table_topicmatch_local_min3.csv
  results/
    openalex_three_path_v1_0/
      journal_parent_publishers.csv
      pathway_flags.csv
      pathway_evidence.csv
      pathway_results.csv
    q3_v5/
      model_results.json
  topics/
    Results/
      results_q1_topic_match_v5.csv
```

Only relevant file directories are mirrored. There is no empty `logic/` or
`nets/` folder on SharePoint: those code directories stay in GitHub.

`event_table_topicmatch_v5.csv` is the current Q3 input. The Min-3 file is
historical and remains only because Q3 notebook step 8 explicitly compares it.
The Intra file is a different descriptive measurement, not the annual Q3 input.
`model_results.json` contains six previously verified v5 fits and author-cluster
Delta intervals from the separate local demo/refit package; it is not a new
bootstrap or the output of a new analysis in this branch.

## One-time setup for each person

Use Python 3.12 or newer. Each person needs permission to read the shared folder.
The code does not borrow another person's browser session or change permissions.

**Browser download (also works in the guest view):** open the team's shared
folder, select **Download** with no individual file selected, and extract the
ZIP. Keep the folder structure intact. Configure `shared_root` as the extracted
directory containing `data-manifest.json`, `data/`, `results/` and `topics/`.
From the repository root, run these commands with your actual extracted path:

```sh
python3 project_data.py configure --shared-root "/path/to/Applied AI Group B Data"
python3 project_data.py fetch --group q3
```

`configure` verifies the files against the repository manifest before saving
their location in the ignored `.shared-data.local.json`. Use `--group q1-q2`
or `--group q3` on `configure` if you downloaded only that group's files.
Then fetch the same group, or open its notebook from `nets/`.
The loader copies and verifies the required inputs; no manual per-file placement
inside the repository is needed. This is a downloaded snapshot, not continuous
synchronization. For updates, download the newly agreed release and verify it
against the corresponding repository manifest.

**Synced folder:** synchronize the SharePoint folder with OneDrive and make its
files available locally. Run the same `configure --shared-root` command with
your own synced **Applied AI Group B Data** folder, the directory containing
`data/` and `results/`. The notebooks reuse that saved location.

Alternatively set the `ACADEMIC_JOURNALS_SHARED_ROOT` environment variable to that
folder. It overrides the local config. There is no workstation path in the
notebook itself.

**Direct downloads:** if the shared files have permitted HTTPS download links,
put them in the ignored local config, keyed by repository-relative file path:

```json
{
  "urls": {
    "data/event_table_topicmatch_v5.csv": "DIRECT_HTTPS_FILE_DOWNLOAD_LINK"
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

Or run Q1/Q2 or Q3 from `nets/`: their first code cell calls the same loader.
Existing input paths are unchanged. The loader checks already present files,
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
python3 project_data.py stage --group all --target /path/to/shared-or-staging-folder
```

Use your actual path. The destination must be the directory that will contain
`data/`, `results/` and `topics/`. `stage` copies only manifest-listed files and
writes a delivery receipt; private notes, source checkouts and temporary files
are never recursively collected. It refuses conflicting destination versions.
If the target is a OneDrive-synced folder, wait for synchronization and check the
files on SharePoint before claiming that the upload completed. Otherwise upload
the prepared directories through SharePoint's folder-upload control.

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
All original analysis code was compared with the branch baseline and is
unchanged. The full statistical notebooks were not rerun for this loader change.

The current local checkout is configured to use a persistent **downloaded
SharePoint snapshot**. It is not an automatically synchronized OneDrive folder.
OneDrive synchronization and access as Felix or another recipient have not been
independently tested. A different user configures their own downloaded or synced
folder using the command above.
The branch and its notebook loader edits are local until explicitly published.

Microsoft documents [SharePoint/OneDrive synchronization](https://support.microsoft.com/en-US/sharepoint/sync/sync-sharepoint-and-teams-files-with-your-computer)
and [Graph file downloads](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0).
