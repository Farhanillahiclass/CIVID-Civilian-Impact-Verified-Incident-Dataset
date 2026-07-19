"""
Deduplication + checksum. Stdlib-only.
Dedup key = sha256(source_url | title | publication_date).
Records sharing a checksum get duplicate_flag=True (kept but flagged).
"""
import hashlib


def make_checksum(source_url: str | None, title: str | None, publication_date: str | None) -> str:
    basis = "|".join([
        (source_url or "").strip().lower(),
        (title or "").strip().lower(),
        (publication_date or "").strip().lower(),
    ])
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def dedupe(records: list[dict]) -> list[dict]:
    """Flag duplicates by checksum; first occurrence stays unflagged."""
    seen: set[str] = set()
    out: list[dict] = []
    for r in records:
        cs = r.get("checksum") or make_checksum(r.get("source_url"), r.get("title"), r.get("publication_date"))
        r["checksum"] = cs
        if cs in seen:
            r["duplicate_flag"] = True
            if r.get("extraction_status") == "ok":
                r["extraction_status"] = "partial"
            r.setdefault("notes", "")
            r["notes"] = (r["notes"] or "") + " [duplicate of prior record]"
        else:
            seen.add(cs)
            r["duplicate_flag"] = False
        out.append(r)
    return out
