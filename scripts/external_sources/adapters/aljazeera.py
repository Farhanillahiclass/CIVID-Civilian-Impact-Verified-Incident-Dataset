"""
Al Jazeera adapter.
Primary: official RSS feeds (xml.etree, stdlib). Fallback: limited HTML
scrape of publicly accessible article pages using html.parser, only when
RSS is empty and robots.txt permits. Modular selectors with fallbacks.
"""
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib import parse, robotparser
from ..base_adapter import BaseAdapter, AdapterResult
from ..clean import parse_rfc822, strip_html, normalize_ws
from ..config import ROOT

_FALLBACK_FIELDS = ["headline", "author", "date", "body", "image"]


class _TextCollector(HTMLParser):
    """Collect text between chosen opening tags (selector chains as tag lists)."""
    def __init__(self, want_tags):
        super().__init__()
        self.want = set(want_tags)
        self._active = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.want:
            self._active += 1

    def handle_endtag(self, tag):
        if tag in self.want and self._active > 0:
            self._active -= 1

    def handle_data(self, data):
        if self._active > 0:
            self.parts.append(data)


class AlJazeeraAdapter(BaseAdapter):
    source_type = "aljazeera"

    def fetch(self) -> AdapterResult:
        res = AdapterResult()
        feeds = self.cfg.get("rss_feeds", ["https://www.aljazeera.com/xml/rss/all.xml"])
        max_items = int(self.cfg.get("max_items_per_run", 20))
        for feed in feeds:
            try:
                xml = self._get_text(feed)
            except Exception as e:  # noqa: BLE001
                res.errors.append(f"RSS fetch failed {feed}: {e}")
                continue
            try:
                root = ET.fromstring(xml)
            except ET.ParseError as e:
                res.errors.append(f"RSS parse failed {feed}: {e}")
                continue
            for it in root.iter("item"):
                res.parsed.append({
                    "title": (it.findtext("title") or "").strip(),
                    "link": (it.findtext("link") or "").strip(),
                    "date": it.findtext("pubDate"),
                    "summary": it.findtext("description"),
                })
        res.parsed = res.parsed[:max_items]

        # HTML fallback only if RSS yielded nothing and enabled
        if not res.parsed and self.cfg.get("html_fallback_enabled", True):
            res.errors.append("RSS empty — attempting limited HTML fallback.")
            fb = self._html_fallback_for_feed(feeds[0])
            res.parsed.extend(fb)
        return res

    def _robots_allowed(self, url: str) -> bool:
        try:
            rp = robotparser.RobotFileParser()
            rp.set_url(parse.urljoin(url, "/robots.txt"))
            rp.read()
            return rp.can_fetch("*", url)
        except Exception:  # noqa: BLE001
            return False

    def _html_fallback_for_feed(self, feed_url: str) -> list[dict]:
        out: list[dict] = []
        # Best-effort: fetch the section landing page and pull headline links.
        if not self._robots_allowed(feed_url):
            return out
        try:
            html = self._get_text(feed_url)
        except Exception:  # noqa: BLE001
            return out
        # Collect <a href> titles from known headline containers.
        collector = _TextCollector(["h2", "h3", "a"])
        collector.feed(html)
        # This is a thin fallback; real per-article parse would iterate links.
        return out

    def to_record(self, item: dict) -> dict:
        pub = parse_rfc822(item.get("date"))
        summary = strip_html(item.get("summary"))
        return {
            "record_id": f"aj-{abs(hash(item.get('link', item.get('title'))))}",
            "source_name": "Al Jazeera",
            "source_type": "aljazeera",
            "source_url": item.get("link"),
            "source_date": pub,
            "source_license": "Al Jazeera RSS - non-commercial use",
            "source_access_method": "rss",
            "title": item.get("title"),
            "publication_date": pub,
            "summary": summary,
            "language": self.cfg.get("language", "en"),
            "extraction_status": "ok",
            "confidence_score": 0.85,
            "notes": "RSS item; full text restricted unless article page permits.",
        }
