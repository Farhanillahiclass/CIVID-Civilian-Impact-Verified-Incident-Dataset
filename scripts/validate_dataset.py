#!/usr/bin/env python3
"""CIVID dataset validator (standard-library only).

Checks every phase's tables for structural integrity:
- required headers present
- duplicate primary keys (within table and, for events/sources, across all phases)
- foreign-key integrity (event->source, person->event, media->event/source)
- controlled-vocabulary compliance (verification_status, confidence_level, victim_role)
- whitespace, date-format, and numeric-field issues

Exit code 0 = no errors (warnings allowed); 1 = at least one error.
Run:  python scripts/validate_dataset.py
"""
from __future__ import annotations
import csv
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
PHASES = ["phase1_palestine", "phase2_sudan", "phase3_iran", "phase4_additional"]

VS_ENUM = {"verified", "estimated", "unverified", "disputed"}
CONF_ENUM = {"high", "medium", "low"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

EVENTS_HEADER = ["record_id", "phase", "country", "conflict_name", "event_id", "event_date",
                 "location", "location_type", "source_id", "fatalities", "injuries", "missing",
                 "verification_status", "confidence_level", "notes"]
SOURCES_HEADER = ["source_id", "source_name", "source_url", "source_type", "source_date",
                  "citation_text", "reliability_score"]

errors: list[str] = []
warnings: list[str] = []


def load(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def load_roles() -> set[str]:
    rows = load(os.path.join(DATA, "reference", "roles.csv"))
    return {r["role_label"] for r in rows} if rows else set()


def check_whitespace(rows, fields, label):
    for i, row in enumerate(rows, start=2):
        for f in fields:
            v = row.get(f)
            if v is not None and v != v.strip():
                warnings.append(f"{label} row {i}: field '{f}' has surrounding whitespace: {v!r}")


def check_dupes(rows, key, label, seen_global=None):
    seen = {}
    for i, row in enumerate(rows, start=2):
        v = (row.get(key) or "").strip()
        if not v:
            continue
        if v in seen:
            errors.append(f"{label}: duplicate {key}='{v}' (rows {seen[v]} and {i})")
        seen[v] = i
        if seen_global is not None:
            if v in seen_global:
                errors.append(f"GLOBAL: duplicate {key}='{v}' ({seen_global[v]} and {label} row {i})")
            else:
                seen_global[v] = f"{label} row {i}"


def main() -> int:
    roles = load_roles()
    if not roles:
        warnings.append("reference/roles.csv missing or empty; victim_role vocab not checked.")

    # event_id is unique PER PHASE; the global key is (phase, event_id).
    # source_id must be globally unique.
    global_source_ids: dict[str, str] = {}

    for phase in PHASES:
        pdir = os.path.join(DATA, phase)
        if not os.path.isdir(pdir):
            continue
        events = load(os.path.join(pdir, "events.csv"))
        persons = load(os.path.join(pdir, "persons.csv"))
        sources = load(os.path.join(pdir, "sources.csv"))
        media = load(os.path.join(pdir, "media.csv"))
        famous = load(os.path.join(pdir, "famous_victims.csv"))

        # header checks (required columns present; order-tolerant)
        if events and not set(EVENTS_HEADER).issubset(events[0].keys()):
            errors.append(f"{phase}/events.csv missing columns: {set(EVENTS_HEADER) - set(events[0].keys())}")
        if sources and not set(SOURCES_HEADER).issubset(sources[0].keys()):
            errors.append(f"{phase}/sources.csv missing columns: {set(SOURCES_HEADER) - set(sources[0].keys())}")

        # duplicates
        check_dupes(events, "event_id", f"{phase}/events")  # unique per phase
        check_dupes(events, "record_id", f"{phase}/events")
        check_dupes(sources, "source_id", f"{phase}/sources", global_source_ids)
        check_dupes(persons, "record_id", f"{phase}/persons")
        check_dupes(media, "media_id", f"{phase}/media")
        check_dupes(famous, "famous_id", f"{phase}/famous_victims")

        src_ids = {(s.get("source_id") or "").strip() for s in sources}
        evt_ids = {(e.get("event_id") or "").strip() for e in events}
        person_rec_ids = {(p.get("record_id") or "").strip() for p in persons}

        # FK + field checks on events
        for i, e in enumerate(events, start=2):
            lbl = f"{phase}/events row {i}"
            sid = (e.get("source_id") or "").strip()
            if not sid:
                warnings.append(f"{lbl}: blank source_id.")
            elif sid not in src_ids:
                errors.append(f"{lbl}: source_id '{sid}' not found in {phase}/sources.csv.")
            vs = (e.get("verification_status") or "").strip()
            if vs and vs not in VS_ENUM:
                errors.append(f"{lbl}: invalid verification_status '{vs}'.")
            cf = (e.get("confidence_level") or "").strip()
            if cf and cf not in CONF_ENUM:
                errors.append(f"{lbl}: invalid confidence_level '{cf}'.")
            d = (e.get("event_date") or "").strip()
            if d and not DATE_RE.match(d):
                errors.append(f"{lbl}: event_date '{d}' not YYYY-MM-DD.")
            for nf in ("fatalities", "injuries", "missing"):
                v = (e.get(nf) or "").strip()
                if v and not v.isdigit():
                    errors.append(f"{lbl}: {nf} '{v}' is not a non-negative integer.")

        # persons FK + role vocab
        for i, p in enumerate(persons, start=2):
            lbl = f"{phase}/persons row {i}"
            eid = (p.get("event_id") or "").strip()
            if eid and eid not in evt_ids:
                errors.append(f"{lbl}: event_id '{eid}' not found in {phase}/events.csv.")
            role = (p.get("victim_role") or "").strip()
            if roles and role and role not in roles:
                errors.append(f"{lbl}: victim_role '{role}' not in controlled vocabulary.")

        # media FK
        for i, m in enumerate(media, start=2):
            lbl = f"{phase}/media row {i}"
            eid = (m.get("event_id") or "").strip()
            if eid and eid not in evt_ids:
                errors.append(f"{lbl}: event_id '{eid}' not found in {phase}/events.csv.")
            msid = (m.get("source_id") or "").strip()
            if msid and msid not in src_ids:
                errors.append(f"{lbl}: source_id '{msid}' not found in {phase}/sources.csv.")

        # famous_victims FK + required provenance (only enforced when rows exist)
        for i, f in enumerate(famous, start=2):
            lbl = f"{phase}/famous_victims row {i}"
            eid = (f.get("event_id") or "").strip()
            if eid and eid not in evt_ids:
                errors.append(f"{lbl}: event_id '{eid}' not found in {phase}/events.csv.")
            pr = (f.get("person_record_id") or "").strip()
            if pr and pr not in person_rec_ids:
                errors.append(f"{lbl}: person_record_id '{pr}' not found in {phase}/persons.csv.")
            fsid = (f.get("source_id") or "").strip()
            if fsid and fsid not in src_ids:
                errors.append(f"{lbl}: source_id '{fsid}' not found in {phase}/sources.csv.")
            if not (f.get("citation_text") or "").strip() or not (f.get("verified_by") or "").strip():
                errors.append(f"{lbl}: famous victim row missing required citation_text and/or verified_by.")
            role = (f.get("victim_role") or "").strip()
            if roles and role and role not in roles:
                errors.append(f"{lbl}: victim_role '{role}' not in controlled vocabulary.")

        check_whitespace(events, EVENTS_HEADER, f"{phase}/events")

    print("=" * 60)
    print("CIVID dataset validation")
    print("=" * 60)
    for w in warnings:
        print(f"  [WARN]  {w}")
    for e in errors:
        print(f"  [ERROR] {e}")
    print("-" * 60)
    print(f"  {len(warnings)} warning(s), {len(errors)} error(s)")
    print("=" * 60)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
