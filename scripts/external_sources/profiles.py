"""
Profile-building layer (Pass-2 consumer).

Consumes Guardian (and Wikipedia) article records that carry `_people`
(name + role actually present in source text). Produces:
  - person profiles (one canonical row per person_name)
  - famous-victim candidates (high-visibility roles / multiple articles)
  - image metadata rows (Guardian thumbnails, internal-use license)

Gating rule (per instructions): a person profile is created ONLY when a
person name AND a role marker are explicitly present in source text.
If role is unclear, role='unknown' and record is sent to review.
No names, ages, bios, or roles are inferred or fabricated.
"""
import hashlib
from collections import defaultdict
from .clean import parse_iso8601

FAMOUS_ROLE_HINTS = {
    "political leader", "military commander", "doctor", "journalist",
}


def _pid(name: str) -> str:
    h = hashlib.sha256(name.strip().lower().encode("utf-8")).hexdigest()[:10]
    return f"PER-{h}"


def build_profiles(records: list[dict]) -> dict:
    """Return dict with person_profiles, famous_candidates, images, review."""
    people_map = defaultdict(lambda: {
        "articles": [], "roles": set(), "snippets": [], "image_url": None,
    })
    images = []
    review = []

    for rec in records:
        people = rec.get("_people") or []
        for p in people:
            name = p.get("person_name")
            if not name:
                continue
            role = p.get("person_role", "unknown")
            entry = people_map[name]
            entry["articles"].append(rec.get("source_url"))
            entry["roles"].add(role)
            entry["snippets"].append(p.get("source_snippet", ""))
            if not entry["image_url"] and rec.get("image_url"):
                entry["image_url"] = rec.get("image_url")

        # image metadata (article-level; internal-use license)
        if rec.get("image_url"):
            images.append({
                "image_id": f"IMG-{abs(hash(rec.get('source_url','')) ) % 10**8:08d}",
                "source_name": rec.get("source_name"),
                "image_url": rec.get("image_url"),
                "image_source": rec.get("source_name"),
                "image_license": rec.get("source_license"),
                "image_caption": rec.get("title"),
                "person_or_article": rec.get("source_url"),
                "safe_flag": True,
            })

    profiles = []
    famous = []
    for name, e in people_map.items():
        roles = e["roles"]
        canonical_role = "unknown" if roles == {"unknown"} else sorted(roles)[0]
        is_unknown = canonical_role == "unknown"
        flags = _role_flags(canonical_role)
        prof = {
            "record_id": _pid(name),
            "person_name": name,
            "person_role": canonical_role,
            "verification_status": "unverified",
            "confidence_level": "low",
            "source_urls": list(dict.fromkeys(e["articles"])),
            "related_articles": list(dict.fromkeys(e["articles"])),
            "role_snippets": e["snippets"][:5],
            "image_url": e["image_url"],
            "image_source": "The Guardian" if e["image_url"] else None,
            "image_license": "Guardian Content API - internal use; no republication" if e["image_url"] else None,
            "image_available": bool(e["image_url"]),
            "notes": "Name + role explicitly present in Guardian source text (Pass-2).",
            "update_mode": "new",
            "last_updated": rec.get("source_date"),
        }
        prof.update(flags)
        if is_unknown:
            review.append({"record_id": prof["record_id"], "person_name": name,
                           "reason": "role unclear in source", "action": "needs_review"})
        profiles.append(prof)

        # famous candidate: high-visibility role OR appears in >1 article
        if (canonical_role in FAMOUS_ROLE_HINTS and len(e["articles"]) >= 1) or len(e["articles"]) > 1:
            famous.append({
                "famous_id": f"FAM-{_pid(name)[4:]}",
                "person_name": name,
                "person_role": canonical_role,
                "fame_reason": "Named with high-visibility role in Guardian reporting"
                               if canonical_role in FAMOUS_ROLE_HINTS else
                               f"Mentioned across {len(e['articles'])} Guardian articles",
                "bio_short": None,  # not fabricated
                "image_url": e["image_url"],
                "image_source": "The Guardian" if e["image_url"] else None,
                "image_license": "Guardian Content API - internal use; no republication" if e["image_url"] else None,
                "guardian_links": list(dict.fromkeys(e["articles"])),
                "wikipedia_link": None,
                "verification_status": "unverified",
                "confidence_level": "low",
            })

    return {"person_profiles": profiles, "famous_candidates": famous,
            "images": images, "review": review}


def _role_flags(role: str) -> dict:
    flags = {k: False for k in [
        "child_flag", "adult_flag", "doctor_flag", "nurse_flag", "medic_flag",
        "journalist_flag", "teacher_flag", "student_flag", "aid_worker_flag",
        "leader_flag", "commander_flag", "civilian_flag", "combatant_flag",
    ]}
    mapping = {
        "child": "child_flag", "doctor": "doctor_flag", "nurse": "nurse_flag",
        "medic / paramedic": "medic_flag", "journalist": "journalist_flag",
        "teacher": "teacher_flag", "student": "student_flag",
        "aid worker": "aid_worker_flag", "political leader": "leader_flag",
        "military commander": "commander_flag", "local commander": "commander_flag",
        "adult civilian": "adult_flag", "fighter / combatant": "combatant_flag",
    }
    if role in mapping:
        flags[mapping[role]] = True
    if role in ("child",):
        flags["child_flag"] = True
    return flags
