#!/usr/bin/env python3
"""CIVID leader image verifier (integrity + provenance check).

Two modes, both standard-library only:

1. LOCAL integrity (works offline):
   For every row in data/leaders.csv where image_available == true, confirm a
   real, decodable image file exists at image_local_path and record its byte
   size + dimensions. Flags any row that claims an image but has no valid file.

2. REMOTE provenance (needs network):
   For every row with an image_url, query the Wikimedia Commons API to confirm
   the file still exists and read back its live license. Reports any mismatch
   between the stored image_license and the live LicenseShortName.

Run:
    python scripts/verify_leader_images.py            # local only
    python scripts/verify_leader_images.py --remote   # also live-check Commons
"""
from __future__ import annotations

import argparse
import csv
import os
import socket

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEADERS = os.path.join(REPO, "data", "leaders.csv")

socket.setdefaulttimeout(8)


def load_rows():
    with open(LEADERS, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def check_local(rows):
    print("== LOCAL IMAGE INTEGRITY ==")
    problems = 0
    for r in rows:
        lid = r.get("leader_id", "?")
        avail = (r.get("image_available") or "").strip().lower() in ("true", "1", "yes")
        if not avail:
            continue
        lp = (r.get("image_local_path") or "").strip()
        path = os.path.join(REPO, lp) if lp else ""
        if not lp or not os.path.isfile(path):
            print(f"  [MISSING] {lid}: image_available=true but no file at '{lp}'")
            problems += 1
            continue
        if Image is None:
            print(f"  [OK-file] {lid}: exists ({os.path.getsize(path)} bytes)")
            continue
        try:
            im = Image.open(path)
            im.verify()
            im2 = Image.open(path)
            im2.load()
            print(f"  [OK] {lid}: {im2.size[0]}x{im2.size[1]}px, {os.path.getsize(path)} bytes")
        except Exception as e:  # noqa: BLE001
            print(f"  [BAD] {lid}: file present but unreadable ({e})")
            problems += 1
    print(f"  local problems: {problems}\n")
    return problems


def check_remote(rows):
    print("== REMOTE PROVENANCE (Wikimedia Commons API) ==")
    import json
    import urllib.request
    from urllib import error

    problems = 0
    titles = []
    mapping = {}
    for r in rows:
        url = (r.get("image_url") or "").strip()
        if not url or "Special:FilePath/" not in url:
            continue
        fn = url.split("Special:FilePath/")[1].split("?")[0]
        t = "File:" + fn
        titles.append(t)
        mapping[t] = r
    if not titles:
        print("  no image_url entries to check")
        return 0
    api = ("https://commons.wikimedia.org/w/api.php?action=query"
           "&prop=imageinfo&iiprop=url|extmetadata|mime&format=json&titles="
           + urllib.parse.quote("|".join(titles)))
    req = urllib.request.Request(api, headers={"User-Agent": "CIVID-verify/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
    except (error.HTTPError, error.URLError) as e:
        print(f"  network error, skipping remote check: {e}")
        return 0
    for pg in data.get("query", {}).get("pages", {}).values():
        title = pg["title"]
        r = mapping.get(title)
        if r is None:
            continue
        lid = r.get("leader_id")
        if "missing" in pg:
            print(f"  [MISSING-REMOTE] {lid}: {title} not found on Commons")
            problems += 1
            continue
        ii = pg["imageinfo"][0]
        lic = ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "?")
        stored = (r.get("image_license") or "").strip()
        flag = "" if stored and stored.split(" ")[0].lower() in lic.lower() else "  <-- LICENSE MISMATCH"
        print(f"  [OK] {lid}: {title} | license '{lic}' (stored: '{stored}'){flag}")
        if flag:
            problems += 1
    print(f"  remote problems: {problems}\n")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--remote", action="store_true", help="also live-check Wikimedia Commons")
    args = ap.parse_args()
    rows = load_rows()
    p = check_local(rows)
    if args.remote:
        p += check_remote(rows)
    else:
        print("(use --remote in a networked environment to verify live Commons provenance)\n")
    return 1 if p else 0


if __name__ == "__main__":
    raise SystemExit(main())
