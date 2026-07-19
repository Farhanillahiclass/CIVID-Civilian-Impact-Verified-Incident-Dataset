"""
Wikipedia / Wikimedia adapter.
Primary: MediaWiki REST summary API. Enrichment: Action API for
categories, links, page id, revision timestamp.
No auth; respects Wikimedia robot/UA policy and maxlag.
"""
from urllib import parse
from ..base_adapter import BaseAdapter, AdapterResult
from ..clean import parse_iso8601, normalize_ws
from ..config import http_get_json

WIKI_REST = "https://en.wikipedia.org/api/rest_v1/page/summary/"
WIKI_ACTION = "https://en.wikipedia.org/w/api.php"


class WikipediaAdapter(BaseAdapter):
    source_type = "wikipedia"

    def fetch(self) -> AdapterResult:
        res = AdapterResult()
        titles = self.cfg.get("titles", [])
        max_items = int(self.cfg.get("max_items_per_run", 20))
        for title in titles[:max_items]:
            try:
                summary = self._get_json(WIKI_REST + parse.quote(title))
            except Exception as e:  # noqa: BLE001 - isolate per page
                res.errors.append(f"{title}: {e}")
                continue
            # Enrich via Action API (batch-safe single call per page)
            enriched = self._enrich(summary.get("title", title))
            summary.update(enriched or {})
            res.parsed.append(summary)
            res.raw_meta.setdefault("ok", []).append(title)
        if not res.parsed and not res.errors:
            res.errors.append("no titles configured or all failed")
        return res

    def _enrich(self, title: str) -> dict | None:
        params = {
            "action": "query", "format": "json",
            "prop": "info|categories|links|pageprops",
            "inprop": "url",
            "rvprop": "timestamp", "rvlimit": 1, "rvdir": "newer",
            "titles": title, "cllimit": "20", "pllimit": "20",
            "maxlag": "5",
        }
        url = f"{WIKI_ACTION}?{parse.urlencode(params)}"
        try:
            data = self._get_json(url)
        except Exception:  # noqa: BLE001
            return None
        pages = (data.get("query", {}).get("pages", {}) or {})
        if not pages:
            return None
        page = next(iter(pages.values()))
        return {
            "pageid": page.get("pageid"),
            "categories": [c["title"] for c in page.get("categories", [])],
            "links": [l["title"] for l in page.get("links", [])],
            "revision_timestamp": (page.get("revisions", [{}])[0].get("timestamp"))
            if page.get("revisions") else None,
            "canonicalurl": page.get("canonicalurl"),
        }

    def to_record(self, item: dict) -> dict:
        title = item.get("title")
        pub = parse_iso8601(item.get("revision_timestamp"))
        return {
            "record_id": f"wiki-{item.get('pageid', hash(title))}",
            "source_name": "Wikipedia",
            "source_type": "wikipedia",
            "source_url": item.get("canonicalurl") or (item.get("content_urls", {})
                                                        .get("desktop", {}).get("page")),
            "source_date": pub,
            "source_license": "CC BY-SA 4.0",
            "source_access_method": "api",
            "title": title,
            "summary": normalize_ws(item.get("extract", "")),
            "page_id": item.get("pageid"),
            "revision_id": None,
            "language": item.get("lang", self.cfg.get("language", "en")),
            "categories": item.get("categories", []),
            "tags": item.get("links", [])[:20],
            "publication_date": pub,
            "extraction_status": "ok",
            "confidence_score": 0.95,
            "notes": "Wikimedia summary + Action API enrichment.",
        }
