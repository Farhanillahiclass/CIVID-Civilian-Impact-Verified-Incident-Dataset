#!/usr/bin/env python3
"""CIVID leaders photo fetcher (standard-library only).

For every row in data/leaders.csv where image_available is true and an image_url
is present, downloads the portrait into a dedicated folder:

    data/leaders_photos/<leader_id>/<leader_id><ext>

and writes the relative path back into the `image_local_path` column of
data/leaders.csv. Already-downloaded files are skipped (idempotent). The local
path is preferred by the dashboards/notebooks so the project is self-contained
and works offline.

Note: Wikimedia's Special:FilePath redirect host is sometimes blocked in
restricted networks, so we resolve the canonical upload.wikimedia.org URL via
the Commons API first, then fall back to the stored image_url.

Run:  python scripts/fetch_leader_photos.py
"""
from __future__ import annotations

import csv
import os
import re
import socket
import time
import json
from urllib import request, error

# Hard global socket timeout so blocked hosts fail fast instead of hanging the run.
socket.setdefaulttimeout(8)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data")
LEADERS_CSV = os.path.join(DATA, "leaders.csv")
PHOTO_ROOT = os.path.join(DATA, "leaders_photos")

HEADERS = {
    "User-Agent": "CIVID-research/1.0 (non-commercial humanitarian research; +https://github.com/)",
    "Accept": "image/jpeg,image/png,image/webp,*/*",
}

EXT_BY_CT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

_url_cache: dict[str, str] = {}


def _api_resolve(title: str):
    """Try en.wikipedia API for a canonical upload.wikimedia.org URL."""
    api = ("https://en.wikipedia.org/w/api.php?action=query"
           "&titles=" + request.quote(title) +
           "&prop=imageinfo&iiprop=url&format=json")
    try:
        req = request.Request(api, headers=HEADERS)
        with request.urlopen(req, timeout=12) as resp:
            data = json.load(resp)
        for pg in data.get("query", {}).get("pages", {}).values():
            ii = pg.get("imageinfo")
            if ii:
                return ii[0]["url"]
    except (error.HTTPError, error.URLError, ValueError, KeyError):
        pass
    return None


def resolve_url(stored: str) -> str:
    """Return a downloadable URL.

    The canonical image_url in leaders.csv points at commons.wikimedia.org
    Special:FilePath, which is blocked in some networks. We instead:
      1. try the en.wikipedia API (works for files mirrored on enwiki), and
      2. try en.wikipedia.org/wiki/Special:FilePath/<name> (redirects to the
         reachable upload.wikimedia.org host).
    Returns '' if nothing resolvable (caller skips with a clear message).
    """
    if stored in _url_cache:
        return _url_cache[stored]
    m = re.search(r"Special:FilePath/([^/?#]+)", stored)
    name = m.group(1) if m else ""
    if name:
        title = "File:" + name
        url = _api_resolve(title)
        if url:
            _url_cache[stored] = url
            return url
        # enwiki Special:FilePath only works for enwiki-local files; for Commons-only
        # files it 404s/hangs, so skip rather than attempt it.
    _url_cache[stored] = ""
    return ""


def load_rows():
    with open(LEADERS_CSV, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def save_rows(rows):
    fields = list(rows[0].keys())
    with open(LEADERS_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def ext_for(url: str, content_type: str) -> str:
    if content_type in EXT_BY_CT:
        return EXT_BY_CT[content_type]
    m = re.search(r"\.([a-zA-Z0-9]+)(?:\?|$)", url)
    if m and m.group(1).lower() in {"jpg", "jpeg", "png", "webp", "gif"}:
        return "." + m.group(1).lower().replace("jpeg", "jpg")
    return ".jpg"


def download(url: str, dest: str) -> bool:
    last = None
    for attempt in range(3):
        try:
            req = request.Request(url, headers=HEADERS)
            with request.urlopen(req, timeout=40) as resp:
                ct = resp.headers.get("Content-Type", "")
                data = resp.read()
            if len(data) < 1500:
                print(f"      [warn] file too small ({len(data)} bytes) — skipping")
                return False
            with open(dest, "wb") as fh:
                fh.write(data)
            return True
        except (error.HTTPError, error.URLError, OSError, ValueError) as e:
            last = e
            time.sleep(2 * (attempt + 1))
    print(f"      [fail] {url} -> {last}")
    return False


def main() -> int:
    rows = load_rows()
    if "image_local_path" not in rows[0].keys():
        for r in rows:
            r["image_local_path"] = ""

    changed = False
    os.makedirs(PHOTO_ROOT, exist_ok=True)

    for r in rows:
        lid = (r.get("leader_id") or "").strip()
        avail = (r.get("image_available") or "").strip().lower()
        url = (r.get("image_url") or "").strip()
        if not lid or avail not in ("true", "1", "yes") or not url:
            continue

        folder = os.path.join(PHOTO_ROOT, lid)
        if os.path.isdir(folder):
            existing = [f for f in os.listdir(folder)
                        if os.path.isfile(os.path.join(folder, f))]
            if existing and not r.get("image_local_path"):
                rel = os.path.relpath(os.path.join(folder, existing[0]), REPO).replace(os.sep, "/")
                r["image_local_path"] = rel
                changed = True
                print(f"[skip] {lid}: already present -> {rel}")
                continue
            if r.get("image_local_path") and os.path.isfile(os.path.join(REPO, r["image_local_path"])):
                print(f"[skip] {lid}: local path recorded and file exists")
                continue

        target = resolve_url(url)
        if not target:
            print(f"[skip] {lid}: could not resolve a downloadable URL (host blocked); "
                  f"set image_url to a direct upload.wikimedia.org link to retry.")
            continue
        print(f"[get ] {lid}: {target}")
        os.makedirs(folder, exist_ok=True)
        ext = ext_for(target, "")
        dest = os.path.join(folder, f"{lid}{ext}")
        if download(target, dest):
            rel = os.path.relpath(dest, REPO).replace(os.sep, "/")
            r["image_local_path"] = rel
            changed = True
            print(f"[ ok ] {lid}: saved {rel}")

    if changed:
        save_rows(rows)
        print("Updated image_local_path in", LEADERS_CSV)
    else:
        print("No photo changes needed.")

    present = sum(1 for r in rows if (r.get("image_local_path") or "").strip())
    total = sum(1 for r in rows if (r.get("image_available") or "").strip().lower() in ("true", "1", "yes"))
    print(f"Photos available: {present}/{total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
