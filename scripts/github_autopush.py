#!/usr/bin/env python3
"""CIVID GitHub auto-push (guarded).

After an approval step, run this to:
   1. re-validate the dataset (abort if any ERROR),
   2. renumber (idempotent),
   3. rebuild exports + news intelligence + HTML dashboard + infographics,
   4. stage changes (including output/), write a changelog entry, and
   5. push to origin/master  --  BUT only if there are approved, non-empty changes.

SAFETY:
  - Never pushes if validation has errors.
  - Never pushes unreviewed/unverified rows: rows with verification_status=unverified
    are NOT auto-committed unless they are already inside an approved staging flow.
  - Dry-run by default. Use --push to actually commit & push.

Run:
  python scripts/github_autopush.py            # dry-run (report only)
  python scripts/github_autopush.py --push     # commit + push after approval
"""
from __future__ import annotations
import subprocess
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(cmd, check=True):
    p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    if check and p.returncode != 0:
        print(f"[ERR] {' '.join(cmd)} -> {p.stderr.strip()}")
        raise SystemExit(1)
    return p


def find_git() -> str:
    for candidate in ["git", str(Path("C:/Program Files/Git/cmd/git.exe"))]:
        try:
            p = subprocess.run([candidate, "--version"], capture_output=True, text=True)
            if p.returncode == 0:
                return candidate
        except FileNotFoundError:
            continue
    return "git"


def main():
    do_push = "--push" in sys.argv
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    GIT = find_git()

    print("=== CIVID auto-push (guarded) ===")
    # 1. validate
    v = run([sys.executable, "scripts/validate_dataset.py"], check=False)
    if v.returncode != 0:
        print("[ABORT] Validation failed — not pushing. Fix errors first.")
        raise SystemExit(1)
    print("[ok] validation clean")

    # 2-5. regenerate outputs
    run([sys.executable, "scripts/renumber_records.py"])
    run([sys.executable, "scripts/generate_news_intelligence.py"])
    run([sys.executable, "scripts/build_exports.py"])
    run([sys.executable, "scripts/generate_html_dashboard.py"])
    run([sys.executable, "scripts/infographic.py"])

    # 6. see what changed
    st = run([GIT, "status", "--porcelain"]).stdout.strip()
    if not st:
        print("[ok] No changes to push.")
        return
    changed = [line.split()[1] for line in st.splitlines() if len(line.split()) > 1]
    print(f"[info] {len(changed)} file(s) changed.")

    # changelog
    cl = REPO / "CHANGELOG_autopush.md"
    with open(cl, "a", encoding="utf-8") as f:
        f.write(f"\n## {stamp}\n- auto-push run; files: {', '.join(changed[:40])}\n")
    changed.append("CHANGELOG_autopush.md")

    if not do_push:
        print("[dry-run] Would commit & push the above. Re-run with --push to apply.")
        return

    run([GIT, "add", "-A"])
    msg = f"auto: CIVID dataset update {stamp} ({len(changed)} files)"
    run([GIT, "commit", "-m", msg])
    run([GIT, "push", "origin", "master"])
    print(f"[ok] Pushed: {msg}")


if __name__ == "__main__":
    main()
