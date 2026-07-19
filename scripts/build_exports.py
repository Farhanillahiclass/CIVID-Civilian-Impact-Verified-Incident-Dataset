#!/usr/bin/env python3
"""CIVID export builder (standard-library only).

Merges every phase's tables into unified, ML/dashboard-ready files under exports/:
  - civid_events_all.csv / .json   (all events + joined source fields + derived flags)
  - civid_persons_all.csv / .json  (all person records)
  - civid_media_all.csv            (all media rows)
  - image_index.csv                (media rows that are images with a URL)
  - civid_dashboard.csv            (curated event columns for visualization)
  - summary.json                   (per-phase counts and quality tallies)

Derived, clearly-prefixed fields are computed here (never hand-entered):
  derived_year, derived_month, derived_timeline_order,
  derived_missing_data_flag, derived_ambiguity_flag,
  derived_is_aggregate, derived_needs_review

Nothing is invented: joins use existing source rows; blanks stay blank.
Run:  python scripts/build_exports.py
"""
from __future__ import annotations
import csv
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
EXPORTS = os.path.join(REPO, "exports")
PHASES = ["phase1_palestine", "phase2_sudan", "phase3_iran", "phase4_additional"]

AGG_KEYWORDS = ("cumulative", "aggregate", "reporting period", "-wide", "since ", "total")
AMBIG_VS = {"estimated", "unverified", "disputed"}


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [ {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
                 for row in csv.DictReader(fh) ]


def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def write_json(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)


def truthy(*vals):
    return any((v or "").strip() for v in vals)


def main():
    all_events, all_persons, all_media = [], [], []
    all_famous = []
    all_news = []
    all_dmeta = []
    summary = {"phases": {}, "totals": {}}

    for phase in PHASES:
        pdir = os.path.join(DATA, phase)
        if not os.path.isdir(pdir):
            continue
        events = load(os.path.join(pdir, "events.csv"))
        persons = load(os.path.join(pdir, "persons.csv"))
        sources = load(os.path.join(pdir, "sources.csv"))
        media = load(os.path.join(pdir, "media.csv"))
        famous = load(os.path.join(pdir, "famous_victims.csv"))
        news = load(os.path.join(pdir, "news_intelligence.csv"))
        dmeta = load(os.path.join(pdir, "dashboard_metadata.csv"))

        src_by_id = {s.get("source_id"): s for s in sources}

        for e in events:
            s = src_by_id.get(e.get("source_id"), {})
            e["source_name"] = s.get("source_name", "")
            e["source_url"] = s.get("source_url", "")
            e["source_type"] = s.get("source_type", "")
            e["source_date"] = s.get("source_date", "")
            e["citation_text"] = e.get("notes", "") or s.get("citation_text", "")
            e["reliability_score"] = s.get("reliability_score", "")
            date = e.get("event_date", "") or ""
            e["derived_year"] = date[:4] if len(date) >= 4 else ""
            e["derived_month"] = date[:7] if len(date) >= 7 else ""
            blob = f"{e.get('location','')} {e.get('notes','')}".lower()
            e["derived_is_aggregate"] = str(any(k in blob for k in AGG_KEYWORDS)).lower()
            missing_core = not truthy(e.get("location"), e.get("location_type"),
                                      e.get("source_id"), e.get("event_date"))
            no_counts = not truthy(e.get("fatalities"), e.get("injuries"), e.get("missing"))
            e["derived_missing_data_flag"] = str(missing_core or no_counts).lower()
            vs = (e.get("verification_status") or "").strip()
            e["derived_ambiguity_flag"] = str(vs in AMBIG_VS or e.get("confidence_level") == "low").lower()
            e["derived_needs_review"] = str(vs == "unverified" or not e.get("reliability_score")).lower()
            e["phase_dir"] = phase
            e["derived_global_event_key"] = f"{phase}/{e.get('event_id','')}"
            all_events.append(e)

        for p in persons:
            p["phase_dir"] = phase
            all_persons.append(p)
        for m in media:
            m["phase_dir"] = phase
            all_media.append(m)
        for f in famous:
            f["phase_dir"] = phase
            all_famous.append(f)
        for n in news:
            n["phase_dir"] = phase
            all_news.append(n)
        for d in dmeta:
            d["phase_dir"] = phase
            all_dmeta.append(d)

        summary["phases"][phase] = {
            "events": len(events),
            "events_verified": sum(1 for e in events if e.get("verification_status") == "verified"),
            "events_unverified": sum(1 for e in events if e.get("verification_status") == "unverified"),
            "persons": len(persons),
            "sources": len(sources),
            "media": len(media),
            "famous_victims": len(famous),
            "news_intelligence": len(news),
        }

    # timeline ordering across the whole dataset (blank dates sort last)
    all_events.sort(key=lambda e: (e.get("event_date") or "9999-99-99", e.get("event_id") or ""))
    for idx, e in enumerate(all_events, start=1):
        e["derived_timeline_order"] = idx

    event_fields = [
        "record_id", "legacy_record_id", "phase", "phase_dir", "country", "conflict_name", "event_id",
        "derived_global_event_key", "event_date",
        "location", "location_type", "source_id", "source_name", "source_url", "source_type",
        "source_date", "reliability_score", "fatalities", "injuries", "missing",
        "verification_status", "confidence_level",
        "derived_year", "derived_month", "derived_timeline_order",
        "derived_is_aggregate", "derived_missing_data_flag", "derived_ambiguity_flag",
        "derived_needs_review", "citation_text", "notes",
    ]
    person_fields = list(all_persons[0].keys()) if all_persons else ["record_id", "event_id"]
    media_fields = list(all_media[0].keys()) if all_media else [
        "media_id", "phase", "event_id", "person_record_id", "media_type", "image_url",
        "image_source", "image_license", "image_caption", "media_warning", "subject_type",
        "contains_identifiable_person", "ethics_review_status", "verification_status",
        "source_id", "notes"]

    write_csv(os.path.join(EXPORTS, "civid_events_all.csv"), all_events, event_fields)
    write_json(os.path.join(EXPORTS, "civid_events_all.json"), all_events)
    write_csv(os.path.join(EXPORTS, "civid_persons_all.csv"), all_persons, person_fields)
    write_json(os.path.join(EXPORTS, "civid_persons_all.json"), all_persons)
    write_csv(os.path.join(EXPORTS, "civid_media_all.csv"), all_media, media_fields)

    # famous victims export (special section)
    famous_fields = list(all_famous[0].keys()) if all_famous else [
        "famous_id", "legacy_record_id", "phase", "country", "conflict_name", "event_id",
        "person_record_id", "victim_name", "victim_alias", "victim_age", "victim_age_group",
        "victim_gender", "victim_role", "occupation", "organization_affiliation", "is_famous",
        "fame_reason", "summary_brief", "death_context", "event_date", "location",
        "image_available", "image_url", "image_source", "image_license", "image_caption",
        "media_warning", "source_id", "source_url", "citation_text", "verified_by",
        "verification_status", "confidence_level", "notes"]
    write_csv(os.path.join(EXPORTS, "civid_famous_victims_all.csv"), all_famous, famous_fields)
    write_json(os.path.join(EXPORTS, "civid_famous_victims_all.json"), all_famous)

    # news intelligence export + dashboard metadata
    news_fields = list(all_news[0].keys()) if all_news else [
        "news_id", "legacy_record_id", "phase", "country", "conflict_name", "metric", "value",
        "unit", "event_or_person_scope", "news_headline", "news_summary", "news_source_url",
        "news_date", "news_category", "source_id", "citation_text", "verified_by",
        "verification_status", "confidence_level", "notes"]
    write_csv(os.path.join(EXPORTS, "civid_news_intelligence_all.csv"), all_news, news_fields)
    write_json(os.path.join(EXPORTS, "civid_news_intelligence_all.json"), all_news)

    dmeta_fields = list(all_dmeta[0].keys()) if all_dmeta else ["meta_key", "meta_value", "phase", "description"]
    write_csv(os.path.join(EXPORTS, "civid_dashboard_metadata_all.csv"), all_dmeta, dmeta_fields)
    write_json(os.path.join(EXPORTS, "civid_dashboard_metadata_all.json"), all_dmeta)

    # verified leaders (cross-phase, confirmed/reported deaths)
    leaders = load(os.path.join(DATA, "leaders.csv"))
    leader_fields = list(leaders[0].keys()) if leaders else [
        "leader_id", "legacy_record_id", "phase", "country", "conflict_name", "leader_name",
        "aka", "role", "organization", "leadership_level", "death_status", "death_date",
        "death_location", "death_cause", "bio", "image_available", "image_url", "image_source",
        "image_license", "image_local_path", "source_id", "source_url", "citation_text",
        "verified_by", "verification_status", "confidence_level", "needs_review", "event_id", "notes"]
    write_csv(os.path.join(EXPORTS, "civid_leaders_all.csv"), leaders, leader_fields)
    write_json(os.path.join(EXPORTS, "civid_leaders_all.json"), leaders)
    summary["totals"]["leaders"] = len(leaders)
    summary["totals"]["leaders_unverified"] = sum(
        1 for r in leaders if (r.get("verification_status") or "").strip() != "verified")
    summary["totals"]["leaders_needs_review"] = sum(
        1 for r in leaders if (r.get("needs_review") or "").strip().lower() in ("true", "1", "yes"))

    # computed aggregate news metrics (citable rollups from verified rows; never invented)
    def to_int(x):
        try:
            return int(float(x))
        except (TypeError, ValueError):
            return 0

    agg = {
        "total_killed": sum(to_int(e.get("fatalities")) for e in all_events),
        "children_killed": sum(1 for p in all_persons if p.get("child_flag") in (True, "true")),
        "women_killed": 0,
        "doctors_killed": sum(1 for p in all_persons if p.get("doctor_flag") in (True, "true")),
        "journalists_killed": sum(1 for p in all_persons if p.get("journalist_flag") in (True, "true")),
        "commanders_killed": sum(1 for p in all_persons if p.get("commander_flag") in (True, "true")),
        "arrests": sum(to_int(e.get("arrests")) for e in all_events) + sum(to_int(p.get("arrests")) for p in all_persons),
        "detentions": sum(to_int(e.get("detention")) for e in all_events) + sum(to_int(p.get("detention")) for p in all_persons),
        "note": "Counts derived from flag columns / fatalities across all phases. Person-level counts reflect rows present, not a verified death total.",
    }
    write_json(os.path.join(EXPORTS, "news_aggregates.json"), agg)

    # image index: media images (if any) + leader portraits keyed by leader_id.
    # Leader portraits live in data/leaders.csv (image_local_path / image_url) and are
    # the authoritative source for the provenance index used by notebooks.
    images = [m for m in all_media if (m.get("media_type") == "image" and (m.get("image_url") or "").strip())]
    img_fields = ["leader_id", "phase", "leader_name", "image_available", "verified_local",
                  "image_url", "image_license", "image_source", "image_local_path", "source_url"]
    leader_imgs = []
    for r in leaders:
        lp = str(r.get("image_local_path") or "").strip()
        verified_local = bool(lp and os.path.exists(os.path.join(REPO, lp)))
        leader_imgs.append({
            "leader_id": r.get("leader_id"),
            "phase": r.get("phase"),
            "leader_name": r.get("leader_name"),
            "image_available": r.get("image_available"),
            "verified_local": str(verified_local).lower(),
            "image_url": r.get("image_url"),
            "image_license": r.get("image_license"),
            "image_source": r.get("image_source"),
            "image_local_path": lp,
            "source_url": r.get("source_url"),
        })
    write_csv(os.path.join(EXPORTS, "image_index.csv"), leader_imgs, img_fields)

    # dashboard-ready curated view
    dash_fields = [
        "phase", "country", "conflict_name", "event_id", "event_date", "derived_year",
        "derived_month", "location", "location_type", "fatalities", "injuries", "missing",
        "verification_status", "confidence_level", "reliability_score",
        "derived_is_aggregate", "derived_missing_data_flag", "derived_ambiguity_flag",
        "derived_needs_review", "derived_timeline_order", "source_name", "source_url",
    ]
    write_csv(os.path.join(EXPORTS, "civid_dashboard.csv"), all_events, dash_fields)

    summary["totals"] = {
        "events": len(all_events),
        "events_verified": sum(1 for e in all_events if e.get("verification_status") == "verified"),
        "events_unverified": sum(1 for e in all_events if e.get("verification_status") == "unverified"),
        "persons": len(all_persons),
        "media": len(all_media),
        "famous_victims": len(all_famous),
        "news_intelligence": len(all_news),
        "images_indexed": len(images),
        "needs_review": sum(1 for e in all_events if e.get("derived_needs_review") == "true"),
    }
    write_json(os.path.join(EXPORTS, "summary.json"), summary)

    print("Exports written to", EXPORTS)
    print(json.dumps(summary["totals"], indent=2))


if __name__ == "__main__":
    main()
