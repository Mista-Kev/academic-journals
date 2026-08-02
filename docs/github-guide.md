# GitHub guide — getting your work into the repo

## One-time setup

1. Install git: https://git-scm.com (Windows: use "Git Bash" afterwards). If you prefer clicking over typing, GitHub Desktop (https://desktop.github.com) does the same things with buttons.
2. Send your GitHub username to Kevin, accept the collaborator invite (arrives by email).
3. Clone the repo (sign in with your GitHub account when asked):
   ```
   git clone https://github.com/Mista-Kev/academic-journals.git
   ```

## Where things go

| What | Where |
|---|---|
| Code / notebooks | your area folder: `fetch/`, `logic/`, `topics/`, `nets/`, `stats/` |
| Generated data (CSV, JSONL, …) | `data/` — **gitignored on purpose, never committed** (GitHub rejects files > 100 MB anyway). Anyone can regenerate them by running the notebook; share big files via Teams/OneDrive |
| Schema docs (what each column means) | `data/schemas/` — one short `.md` per table |
| Decisions | `docs/decisions.md` |

## Everyday flow

```
git pull origin main                       # 1. start up to date
git switch -c fetch/openalex-dataset       # 2. new branch: area/short-topic
# 3. add or edit your files, e.g. fetch/OpenAlex_AI_Dataset_v1_0.ipynb
git status                                 # 4. check: only code/docs listed, NO data files
git add fetch/
git commit -m "Add OpenAlex dataset notebook v1.0"
git push -u origin fetch/openalex-dataset  # 5. upload the branch
```

Then open github.com → the repo shows a "Compare & pull request" button → create the pull request → another team member reads it → merge. Small steps beat big drops: one topic per branch, one PR per topic.

## Example: the OpenAlex v1.0 dataset

- `OpenAlex_AI_Dataset_v1_0.ipynb` → `fetch/` (this goes in the PR)
- a short `data/schemas/openalex_ai_semiclean_v1_0.md` listing the CSV columns (also in the PR)
- `openalex_ai_raw_v1_0.jsonl` + `openalex_ai_semiclean_v1_0.csv` → your local `data/` folder, shared via Teams — **not** in git. Keep the raw JSONL safe (OneDrive is fine): it is the frozen v1.0 artifact, and a re-download later will not be identical because OpenAlex updates continuously.

## Rules of thumb

- Everything in English (code comments, commits, PRs).
- Never commit `.env`, API keys, or anything from `data/` — if `git status` lists a data file, stop and ask.
- Unsure about anything git: post in Teams before force-anything.
