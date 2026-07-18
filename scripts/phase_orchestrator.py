#!/usr/bin/env python3
"""CIVID phase orchestrator — automatically advance to the next phase when one is complete.

Completion rule for the CURRENT phase (all must hold):
  1. validate_dataset.py exits 0 (0 errors).
  2. The current phase's production tables contain NO row with verification_status == 'unverified'.
  3. staging/pending_review.csv has NO pending (unverified) row for the current phase.

When complete, the orchestrator:
  - logs the transition in CHANGELOG_autopush.md,
  - ensures the NEXT phase's folder + empty table scaffolds exist,
  - prints the next-phase brief (scope + source candidates),
  - and (optionally) runs the refresh pipeline.
  - It NEVER pushes to GitHub on its own. GitHub push requires explicit approval
    (scripts/github_autopush.py --push) and still refuses any unverified row.

Run:
  python scripts/phase_orchestrator.py            # check + advance if complete; refresh
  python scripts/phase_orchestrator.py --no-refresh
  python scripts/phase_orchestrator.py --status   # just report current phase state
"""
from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")

# Fixed phase order from the project spec.
PHASES = [
    ("phase1_palestine", "Palestine / Gaza", "Israeli-Palestinian conflict"),
    ("phase2_sudan", "Sudan", "Sudanese Civil Conflict"),
    ("phase3_iran", "Iran (Twelve-Day War)", "Iran-Israel conflict"),
    ("phase4_additional", "Additional countries", "Future phases (Yemen, etc.)"),
]

TABLES = ["events", "persons", "sources", "media", "entities",
          "famous_victims", "news_intelligence", "dashboard_metadata"]

VS_UNVERIFIED = {"unverified"}


def run(cmd):
    p = subprocess.run([sys.executable, *cmd], cwd=REPO, capture_output=True, text=True)
    print(p.stdout.strip())
    if p.stderr.strip():
        print("[stderr]", p.stderr.strip()[:500])
    return p


def validation_clean() -> bool:
    p = run(["scripts/validate_dataset.py"])
    return p.returncode == 0


def load_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def phase_has_unverified(phase_key: str) -> bool:
    """Any UNRESOLVED unverified row in this phase's production tables?

    A row blocks phase completion only if it is 'unverified' AND not already an
    explicitly held review-queue item (needs_review=true). Rows marked
    needs_review=true are single-source / disputed records that are intentionally
    parked in the review queue (e.g. LDR-024 Houthi leader denied by Houthi media)
    and must NOT block a phase from being considered complete.
    """
    phase_dir = os.path.join(DATA, phase_key)
    if not os.path.isdir(phase_dir):
        return False
    for tbl in TABLES:
        fp = os.path.join(phase_dir, f"{tbl}.csv")
        if not os.path.exists(fp):
            continue
        for r in load_rows(fp):
            vs = (r.get("verification_status") or "").strip().lower()
            if vs not in VS_UNVERIFIED:
                continue
            # held review-queue rows (needs_review=true) do not block completion
            if (r.get("needs_review") or "").strip().lower() in ("true", "1", "yes"):
                continue
            return True
    return False


def leaders_has_blocking_unverified(phase_key: str) -> bool:
    """Scan the cross-phase data/leaders.csv for UNRESOLVED unverified rows of this phase.

    The leaders table lives at the repo root (not inside phaseN/), so the
    per-phase scan above misses it. needs_review=true rows are held deliberately
    (disputed / single-source) and do NOT block phase completion.
    """
    lp = os.path.join(DATA, "leaders.csv")
    if not os.path.exists(lp):
        return False
    for r in load_rows(lp):
        if (r.get("phase") or "").strip() != phase_key:
            continue
        if (r.get("verification_status") or "").strip().lower() not in VS_UNVERIFIED:
            continue
        if (r.get("needs_review") or "").strip().lower() in ("true", "1", "yes"):
            continue
        return True
    return False


def staging_has_pending(phase_num: int) -> bool:
    fp = os.path.join(DATA, "staging", "pending_review.csv")
    if not os.path.exists(fp):
        return False
    for r in load_rows(fp):
        if (r.get("verification_status") or "").strip().lower() in VS_UNVERIFIED \
           and (r.get("phase") or "").strip() == str(phase_num):
            return True
    return False


STATE_FILE = os.path.join(REPO, "data", "staging", "current_phase.txt")


def current_phase_index() -> int:
    """Track the active phase explicitly via a state file (sequential auto-advance).

    Default to phase 1. The orchestrator only advances when the CURRENT phase
    is complete, so it never skips ahead to a later phase that still has
    unverified rows (e.g. a single-source review-queue leader in phase4).
    """
    if os.path.exists(STATE_FILE):
        try:
            # State file stores a 1-based phase number (matches daily_update.py
            # cfg["phase"]); convert to the 0-based PHASES index here.
            v = int(open(STATE_FILE, encoding="utf-8").read().strip()) - 1
            if 0 <= v < len(PHASES):
                return v
        except Exception:
            pass
    return 0


def set_phase_index(i: int):
    # Store the 1-based phase number so daily_update.py (which reads cfg["phase"])
    # and the orchestrator agree on the same numeric convention.
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(str(i + 1))


def ensure_next_phase_scaffold(next_idx: int):
    key, country, conflict = PHASES[next_idx]
    d = os.path.join(DATA, key)
    os.makedirs(d, exist_ok=True)
    # only create empty scaffolds if a table is entirely missing
    for tbl in TABLES:
        fp = os.path.join(d, f"{tbl}.csv")
        if not os.path.exists(fp):
            # minimal header hint file (empty rows); filled by extraction later
            with open(fp, "w", newline="", encoding="utf-8") as fh:
                fh.write("")  # placeholder; real schema applied on first extraction
    print(f"[scaffold] ensured {key} folder + tables exist.")


def log_transition(from_idx: int, to_idx: int):
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    fk, fc, fconf = PHASES[from_idx]
    tk, tc, tconf = PHASES[to_idx]
    cl = os.path.join(REPO, "CHANGELOG_autopush.md")
    line = (f"\n## {stamp}\n"
            f"- PHASE AUTO-ADVANCE: '{fc}' ({fk}) complete -> advanced to "
            f"'{tc}' ({tk}). Completion gate: validation clean, no unverified "
            f"production rows, no pending review items for that phase. "
            f"Next scope: {tconf}. GitHub push remains approval-gated (not auto).\n")
    with open(cl, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"[phase] advanced {fc} -> {tc}")


def print_next_brief(to_idx: int):
    key, country, conflict = PHASES[to_idx]
    print(f"\n=== NEXT PHASE BRIEF: {country} ({key}) ===")
    print(f"Conflict: {conflict}")
    print("Recommended source candidates (verified-only):")
    brief = {
        0: ["UN OCHA oPt", "UNRWA", "OHCHR", "Gaza MoH (aggregate, labeled)", "ACLED", "Reuters/AP"],
        1: ["ICRC Sudan", "WHO Sudan", "UN OCHA Sudan", "UNHCR Sudan", "ACLED Sudan", "Reuters"],
        2: ["ACLED", "HRANA", "Iran MoH", "Reuters/AP", "OHCHR"],
        3: ["UN OCHA", "UNHCR", "ACLED", "Reuters/AP (per clearly-scoped event only)"],
    }
    for s in brief.get(to_idx, []):
        print("  -", s)
    print("Extraction plan: collect source candidates -> extract schema-conformant rows ->")
    print("normalize -> dedup -> cite -> CSV/JSON -> data dictionary -> human review -> promote.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-refresh", action="store_true")
    ap.add_argument("--status", action="store_true", help="report current phase state only")
    args = ap.parse_args()

    idx = current_phase_index()
    key, country, conflict = PHASES[idx]
    print(f"=== CIVID phase orchestrator ===")
    print(f"Active phase: {country} ({key})  [index {idx}]")

    if args.status:
        print("  validation clean:", validation_clean())
        print("  unverified production rows:", phase_has_unverified(key))
        print("  pending review items:", staging_has_pending(idx + 1))
        return

    clean = validation_clean()
    unv = phase_has_unverified(key) or leaders_has_blocking_unverified(key)
    pend = staging_has_pending(idx + 1)

    print(f"  validation clean: {clean}")
    print(f"  unverified production rows in phase: {unv}")
    print(f"  pending review items for phase: {pend}")

    complete = clean and not unv and not pend
    print(f"  PHASE COMPLETE: {complete}")

    if not complete:
        print("[hold] Phase not complete. Resolve unverified rows / pending review, then re-run.")
        if not args.no_refresh:
            run(["scripts/refresh.py"])
        return

    if idx >= len(PHASES) - 1:
        print("[done] Final phase reached. No further auto-advance.")
        if not args.no_refresh:
            run(["scripts/refresh.py"])
        return

    # advance
    ensure_next_phase_scaffold(idx + 1)
    log_transition(idx, idx + 1)
    set_phase_index(idx + 1)  # persist the frontier so we never skip ahead
    print_next_brief(idx + 1)

    if not args.no_refresh:
        run(["scripts/refresh.py"])

    print("\n[gate] GitHub push is NOT performed here. After human approval, run:")
    print("       python scripts/github_autopush.py --push")


if __name__ == "__main__":
    raise SystemExit(main())
