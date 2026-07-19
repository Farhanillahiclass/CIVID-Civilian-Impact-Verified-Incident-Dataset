"""
Pipeline orchestration. Stdlib-only.
Layers: ingest (adapter.fetch) -> parse (adapter.to_record)
-> clean -> validate -> dedupe -> export.
Source failures are isolated; the whole run never aborts on one failure.
"""
from datetime import datetime, timezone

from .config import load_cfg, load_dotenv
from .throttle import TokenBucket
from .clean import strip_html, parse_iso8601, parse_rfc822, normalize_ws
from .dedupe import dedupe, make_checksum
from .validate import validate_record, load_schema
from .export import export, export_profiles, log_failure
from .adapters import ADAPTERS
from .profiles import build_profiles

load_dotenv()


def _clean_record(r: dict) -> dict:
    for k in ("title", "subtitle", "author", "summary", "section", "image_caption", "notes"):
        if isinstance(r.get(k), str):
            r[k] = normalize_ws(r[k])
    if isinstance(r.get("summary"), str):
        r["summary"] = strip_html(r["summary"])
    # normalize dates
    for dk in ("source_date", "publication_date"):
        if r.get(dk):
            r[dk] = parse_iso8601(r[dk]) or r[dk]
    return r


def run_source(name: str) -> list[dict]:
    if name not in ADAPTERS:
        log_failure(name, f"unknown source '{name}'")
        return []
    cfg = load_cfg(name)
    if cfg.get("enabled") is False:
        return []
    rate = float(cfg.get("request_rate_per_sec", 1.0))
    limiter = TokenBucket(rate=rate, capacity=max(1.0, rate * 5))
    adapter = ADAPTERS[name](cfg=cfg, limiter=limiter)

    try:
        res = adapter.fetch()
    except Exception as e:  # noqa: BLE001 - total isolation
        log_failure(name, f"unhandled fetch error: {e}")
        return []

    if res.errors and not res.parsed:
        log_failure(name, "; ".join(res.errors))
        return []

    schema = load_schema()
    records: list[dict] = []
    for item in res.parsed:
        try:
            rec = adapter.to_record(item)
        except Exception as e:  # noqa: BLE001
            log_failure(name, f"to_record error: {e}")
            continue
        rec = _clean_record(rec)
        rec["checksum"] = make_checksum(rec.get("source_url"), rec.get("title"), rec.get("publication_date"))
        ok, errs = validate_record(rec, schema)
        if not ok:
            rec["extraction_status"] = "partial"
            rec["confidence_score"] = min(rec.get("confidence_score", 0.5), 0.5)
            rec["notes"] = (rec.get("notes") or "") + " [validation: " + "; ".join(errs) + "]"
        records.append(rec)

    records = dedupe(records)
    return records


def run_all() -> list[dict]:
    all_records: list[dict] = []
    for name in ADAPTERS:
        try:
            all_records += run_source(name)
        except Exception as e:  # noqa: BLE001
            log_failure(name, f"pipeline error: {e}")
    run_meta = {
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "all",
        "status": "ok",
        "notes": f"{len(all_records)} records extracted across {len(ADAPTERS)} sources.",
    }
    export(all_records, run_meta)
    # Pass-2 profile outputs (only from records carrying explicit person mentions)
    profile_outputs = build_profiles(all_records)
    export_profiles(profile_outputs)
    return all_records
