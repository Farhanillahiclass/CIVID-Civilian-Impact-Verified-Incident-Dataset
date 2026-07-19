"""
CLI entrypoint for the external source extractor.

Usage:
    python -m scripts.external_sources run --source all
    python -m scripts.external_sources run --source guardian
    python -m scripts.external_sources run --source wikipedia,aljazeera

Outputs: data/staging/external_records.{csv,json}
         data/staging/external_review_queue.csv
         data/staging/external_changelog.csv
"""
import sys
from .pipeline import run_source, run_all
from .adapters import ADAPTERS


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    cmd = argv[0] if argv else "run"
    args = argv[1:]

    source = "all"
    for a in args:
        if a.startswith("--source"):
            source = a.split("=", 1)[1] if "=" in a else (args[args.index(a) + 1] if args.index(a) + 1 < len(args) else "all")

    if cmd == "run":
        if source == "all":
            records = run_all()
        else:
            names = [s.strip() for s in source.split(",") if s.strip() in ADAPTERS]
            records = []
            for n in names:
                records += run_source(n)
            from .export import export, export_profiles
            from datetime import datetime, timezone
            from .profiles import build_profiles
            export(records, {
                "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "source": source, "status": "ok",
                "notes": f"{len(records)} records from {names}.",
            })
            export_profiles(build_profiles(records))
        print(f"[done] {len(records)} records written to data/staging/external_records.*")
        review = [r for r in records if r.get("extraction_status") in ("partial", "failed")]
        if review:
            print(f"[review] {len(review)} record(s) need human review (see external_review_queue.csv)")
        return 0

    print(__doc__)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
