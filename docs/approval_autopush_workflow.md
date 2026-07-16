# CIVID — Approval Workflow & GitHub Auto-Push

## Approval workflow (human-in-the-loop)

1. **Extract** new candidate rows via `scripts/daily_update.py` → `data/staging/pending_review.csv`
   (`verification_status=unverified`, `confidence_level=low`).
2. **Review** each candidate: open the source URL, confirm the fact, fill `citation_text`,
   set real `verification_status`/`confidence_level`. Reject unsafe/unverifiable leads to
   `data/staging/rejected.csv` with a reason.
3. **Promote** reviewed rows with `scripts/promote_entry.py` (writes a verified row + source).
4. **Validate + renumber + export** (`validate_dataset.py`, `renumber_records.py`,
   `build_exports.py`).
5. **Approve & publish** with `scripts/github_autopush.py --push`.

Never auto-commit `unverified` rows to the main dataset. The "needs review" flag in exports
(`derived_needs_review`) tracks the queue.

## GitHub auto-push (`scripts/github_autopush.py`)

Pipeline (all local, reproducible):
```
validate_dataset.py  ->  renumber_records.py  ->  build_exports.py
  ->  generate_news_intelligence.py  ->  generate_html_dashboard.py
  ->  git add -A  ->  commit  ->  push origin master
```

### Safety guarantees
- **Aborts** if `validate_dataset.py` reports any ERROR.
- **Dry-run by default**; actual commit/push only with `--push`.
- Writes a `CHANGELOG_autopush.md` entry per run.
- Does not fabricate or auto-promote unverified data.

### Scheduling (optional)
Windows Task Scheduler / cron calling `python scripts/github_autopush.py --push` daily, after
the human review step. Recommended: run the review in the morning, the auto-push in the
evening, so only approved changes reach `master`.

> Note: git is invoked via the `git` on PATH. If your environment keeps git elsewhere
> (e.g. `C:\Program Files\Git\cmd\git.exe`), set the `GIT` variable at the top of the script.
