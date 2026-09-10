# Using the shared data

Our data are in **Applied AI Group B Data / official-v5-2026-09-07-abcd-v1** on
SharePoint. The folder contains 13 data files, about 2.65 GB, with the same A/B/C
paths as the repository. `FILES.md` lists them; [data-manifest.json](../../data-manifest.json)
records their sizes and checksums.

## How to use it

Download and extract that subfolder, or synchronize it with OneDrive and make
the files available locally. Use the folder containing A/B/C and `START_HERE.txt`,
not the parent folder containing both old and new releases.

With Python 3.12 or newer, run these commands from the repository root:

```sh
python3 -m pip install -r requirements.txt
python3 project_data.py configure --shared-root "/path/to/official-v5-2026-09-07-abcd-v1"
python3 demo.py q1-q2
python3 demo.py q3
```

Replace the example path with your own. Configuration is saved locally and is
not committed to Git. Both notebooks use this setting, copy the required files
into the repository and check their sizes and SHA-256 hashes before calculating.
Once loaded, those files can be used offline. A browser download is a snapshot;
OneDrive synchronization is managed by OneDrive, not by the notebooks.

If you downloaded only one analysis's inputs, configure that group:

```sh
python3 project_data.py configure --shared-root "/path/to/your/folder" --group q3
```

Use `--group q1-q2` for Q1/Q2. To see the required files, run
`python3 project_data.py list --group q3` or replace `q3` with `q1-q2`.

## If loading fails

- **Missing file:** check that you selected the folder containing A/B/C and that
  OneDrive has downloaded the files locally.
- **Wrong size or checksum:** keep any intentional local edits, then obtain the
  matching file from the shared release. The loader will not overwrite a different
  local file. Do not change the manifest to accept it.
- **Sign-in or access problem:** open SharePoint in your browser and download the
  files with your own account. The loader does not handle Microsoft login.
- **Conflicting source setting:** unset `ACADEMIC_JOURNALS_SHARED_ROOT` before
  saving a different folder with `configure`.
- **Hard-link support error:** use a writable local filesystem that supports hard
  links for the repository/cache, then read from your downloaded or synced source.
  Direct staging on every cloud or network filesystem is not supported.

Git preserves the exact bytes of tracked reference CSVs through `.gitattributes`.
If an older checkout converted their line endings, preserve your edits before
restoring those files or obtaining the matching shared copies.

## What the files mean

Q1/Q2 use the semiclean paper corpus, publisher mapping and pathway flags.
Q3 uses the annual Python table and Pierre's official v5 topic table; the older
Min-3 table is used only for the historical comparison in step 8.

The Q1 Intra file describes topic similarity within observed author-journal groups;
it does not adjust the Q1/Q2 ratios. The Q3 `model_results.json` contains reference
calculations from `refit.py` in a separate offline package. That producer is not
included here. The notebook calculates its own estimates; the JSON also provides
reference delta intervals for the sensitivity fits.

For exact inputs and outputs, see [the analysis description](analysis-interfaces.md).
Rebuilding the embeddings needs the additional environment described in
[C's README](../../C_topic_match/README.md).

## Sharing a new data version

The notebooks calculate locally. They do not overwrite the team's SharePoint files.
To prepare a release from the files listed in the manifest:

```sh
python3 project_data.py verify --group all
python3 project_data.py prepare-release --target /path/to/new-release
python3 project_data.py verify-release --target /path/to/new-release
```

Choose a dedicated empty folder outside the repository, which must not contain the
repository either. Preparation includes the 13 data files and four accompanying
files: `START_HERE.txt`, `FILES.md`, `data-manifest.json` and a delivery receipt.
It rejects differing files or unexpected content; ordinary Finder/Windows metadata
files are tolerated. A folder prepared with `stage --group ...` is only a subset.
Use a new folder for a complete release rather than deleting the subset's receipt.

Publish the matching code, upload the complete folder under a new release name,
then download it separately and run `verify-release` on that download. Keep the
previous release available. Both data and generated metadata are checked exactly:
changes to the manifest or generated instructions require a new delivery folder.

## What we checked

On 10 September we downloaded all 13 data files and four accompanying files again.
Their sizes and hashes matched, and both full analyses reproduced the previous
outputs. Access through another person's account and automatic OneDrive sync were
not tested. [The check record](validation.md) gives the details and software tests.

<details>
<summary>Other loader options and older folder layouts</summary>

`python3 project_data.py --help` lists the commands. Besides `q1-q2` and `q3`,
file groups include `logic`, `parity`, `corpus`, `topics`, `outputs`, `sensitivity`
and `all`. `topics` supplies data, not the full DuckDB/GPU environment.

`ACADEMIC_JOURNALS_SHARED_ROOT` overrides saved configuration.
`fetch --shared-root` overrides both for that call without changing the saved path.
Direct HTTPS file URLs can be set in the local config under `urls`, keyed by
repository-relative file path. [shared-data.example.json](../../shared-data.example.json)
shows the config fields. Folder-view links and
Microsoft login pages are not file downloads. Keep credentials and signed URLs
out of Git.

The [migration map](layout-migration.json) records the old paths. The loader tries
the new path first, then the explicit legacy path if the new one is absent. A
mismatched new file is rejected. For configured URL keys, the new key similarly
wins over the legacy key; an invalid new link does not trigger fallback.

</details>
