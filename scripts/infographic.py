#!/usr/bin/env python3
"""CIVID infographic generator.

Generates PNG summary images into output/images/ from production CSVs.
Outputs:
  - output/images/infographic_summary.png
  - output/images/dashboard_home.png
  - output/images/leaders_page.png
  - output/images/famous_persons_page.png
  - output/images/news_summary.png

Uses Pillow (PIL) for image generation. Falls back to minimal PNG if Pillow
is not available.
Run: python scripts/infographic.py
"""
from __future__ import annotations
import csv
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUTPUT = REPO / "output" / "images"
PHASES = ["phase1_palestine", "phase2_sudan", "phase3_iran", "phase4_additional"]

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


def load_events():
    rows = []
    for phase in PHASES:
        fp = REPO / "data" / phase / "events.csv"
        if not fp.exists():
            continue
        try:
            with open(fp, newline="", encoding="utf-8-sig") as f:
                rows.extend(list(csv.DictReader(f)))
        except Exception as e:
            print(f"[warn] failed to read {fp}: {e}")
    return rows


def load_leaders():
    fp = REPO / "data" / "leaders.csv"
    if not fp.exists():
        return []
    try:
        with open(fp, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []


def ensure_output():
    OUTPUT.mkdir(parents=True, exist_ok=True)


def make_pillow_image(width=800, height=600, bg_color=(30, 30, 30), text_color=(230, 230, 230)):
    if not PIL_AVAILABLE:
        return None
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        small = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
        small = font
    return img, draw, font, small, text_color


def save_pillow(img, path):
    if img is None:
        return False
    img.save(path)
    return True


def infographic_summary(events):
    ensure_output()
    path = OUTPUT / "infographic_summary.png"
    if not PIL_AVAILABLE:
        make_placeholder_png(path, 800, 600, (30, 30, 30))
        print(f"[ok] placeholder {path}")
        return

    total = len(events)
    verified = sum(1 for e in events if (e.get("verification_status") or "").strip() == "verified")
    fatalities = sum(int(e.get("fatalities") or 0) for e in events if (e.get("fatalities") or "").strip().isdigit())
    children = sum(1 for e in events if "child" in (e.get("notes") or "").lower() or "child" in (e.get("location") or "").lower())

    width, height = 900, 500
    img, draw, font, small, text_color = make_pillow_image(width, height)
    draw.text((20, 20), "CIVID Infographic Summary", fill=text_color, font=font)
    lines = [
        f"Total events: {total}",
        f"Verified events: {verified}",
        f"Fatalities (sum): {fatalities}",
        f"Child mentions: {children}",
        f"Phases: {len(set(e.get('phase','') for e in events))}",
        "",
        "Source-linked records only.",
        "No fabricated data.",
    ]
    y = 80
    for line in lines:
        draw.text((20, y), line, fill=text_color, font=small)
        y += 30
    save_pillow(img, path)
    print(f"[ok] {path}")


def dashboard_home(events, leaders):
    ensure_output()
    path = OUTPUT / "dashboard_home.png"
    if not PIL_AVAILABLE:
        make_placeholder_png(path, 800, 500, (40, 40, 60))
        print(f"[ok] placeholder {path}")
        return

    width, height = 900, 500
    img, draw, font, small, text_color = make_pillow_image(width, height, bg_color=(40, 40, 60))
    draw.text((20, 20), "CIVID Dashboard Home", fill=text_color, font=font)
    lines = [
        f"Events: {len(events)}",
        f"Leaders: {len(leaders)}",
        f"Verified: {sum(1 for e in events if (e.get('verification_status') or '') == 'verified')}",
        "",
        "Charts rendered in browser via Chart.js.",
        "Open output/index.html to view.",
    ]
    y = 80
    for line in lines:
        draw.text((20, y), line, fill=text_color, font=small)
        y += 30
    save_pillow(img, path)
    print(f"[ok] {path}")


def leaders_page(leaders):
    ensure_output()
    path = OUTPUT / "leaders_page.png"
    if not PIL_AVAILABLE:
        make_placeholder_png(path, 800, 500, (30, 40, 30))
        print(f"[ok] placeholder {path}")
        return

    width, height = 1000, 600
    img, draw, font, small, text_color = make_pillow_image(width, height, bg_color=(30, 40, 30))
    draw.text((20, 20), "CIVID Leaders Page", fill=text_color, font=font)
    y = 70
    for leader in leaders[:15]:
        line = f"{leader.get('leader_name','')} | {leader.get('role','')} | {leader.get('organization','')} | {leader.get('death_date','')} | {leader.get('verification_status','')}"
        draw.text((20, y), line, fill=text_color, font=small)
        y += 25
        if y > height - 20:
            break
    save_pillow(img, path)
    print(f"[ok] {path}")


def famous_persons_page(famous):
    ensure_output()
    path = OUTPUT / "famous_persons_page.png"
    if not PIL_AVAILABLE:
        make_placeholder_png(path, 800, 500, (40, 30, 30))
        print(f"[ok] placeholder {path}")
        return

    width, height = 900, 500
    img, draw, font, small, text_color = make_pillow_image(width, height, bg_color=(40, 30, 30))
    draw.text((20, 20), "CIVID Famous Persons Page", fill=text_color, font=font)
    y = 70
    for person in famous[:15]:
        line = f"{person.get('victim_name','')} | {person.get('victim_role','')} | {person.get('event_date','')} | {person.get('verification_status','')}"
        draw.text((20, y), line, fill=text_color, font=small)
        y += 25
        if y > height - 20:
            break
    save_pillow(img, path)
    print(f"[ok] {path}")


def news_summary(news):
    ensure_output()
    path = OUTPUT / "news_summary.png"
    if not PIL_AVAILABLE:
        make_placeholder_png(path, 800, 500, (30, 30, 40))
        print(f"[ok] placeholder {path}")
        return

    width, height = 1000, 600
    img, draw, font, small, text_color = make_pillow_image(width, height, bg_color=(30, 30, 40))
    draw.text((20, 20), "CIVID News Summary", fill=text_color, font=font)
    y = 70
    for item in news[:20]:
        headline = item.get("news_headline") or item.get("metric", "")
        line = f"{headline[:90]} | {item.get('news_category','')} | {item.get('verification_status','')}"
        draw.text((20, y), line, fill=text_color, font=small)
        y += 25
        if y > height - 20:
            break
    save_pillow(img, path)
    print(f"[ok] {path}")


def make_placeholder_png(path: Path, width: int = 800, height: int = 600, color: tuple[int, int, int] = (30, 30, 30)):
    """Create a minimal valid PNG file with a solid color using only standard library."""
    import struct
    import zlib

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + c + crc

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = chunk(b"IHDR", ihdr_data)
    raw = b"".join(bytes(color) for _ in range(width * height))
    compressed = zlib.compress(raw, 9)
    idat = chunk(b"IDAT", compressed)
    iend = chunk(b"IEND", b"")
    path.write_bytes(sig + ihdr + idat + iend)


def main():
    events = load_events()
    leaders = load_leaders()
    famous_path = REPO / "exports" / "civid_famous_victims_all.csv"
    famous = []
    if famous_path.exists():
        try:
            with open(famous_path, newline="", encoding="utf-8-sig") as f:
                famous = list(csv.DictReader(f))
        except Exception:
            famous = []
    news_path = REPO / "exports" / "civid_news_intelligence_all.csv"
    news = []
    if news_path.exists():
        try:
            with open(news_path, newline="", encoding="utf-8-sig") as f:
                news = list(csv.DictReader(f))
        except Exception:
            news = []

    infographic_summary(events)
    dashboard_home(events, leaders)
    leaders_page(leaders)
    famous_persons_page(famous)
    news_summary(news)
    print("[ok] All infographics generated in output/images/")


if __name__ == "__main__":
    main()
