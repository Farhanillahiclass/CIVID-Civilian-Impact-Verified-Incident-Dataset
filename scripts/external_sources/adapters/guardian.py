"""
The Guardian Content API adapter.
Requires GUARDIAN_API_KEY (read from env / .env). If absent, the source
is skipped cleanly without breaking the run.

Two-pass design:
  Pass 1 (article discovery): paginated search, scoped by config query +
      pillar. Articles are kept only if their text matches >=1 role keyword
      (role_keywords) -> "relevant" set.
  Pass 2 (named-entity extraction): only relevant articles are scanned for
      person names using a transparent, auditable rule-based extractor that
      requires a name to appear adjacent to a role marker in the source text.
      No names are inferred or fabricated.

Body text is stored only for internal use per API terms; flagged in notes.
"""
import os
import re
from urllib import parse
from ..base_adapter import BaseAdapter, AdapterResult
from ..clean import parse_iso8601, strip_html, normalize_ws
from ..config import load_dotenv, HEADERS

load_dotenv()

# Transparent role-marker regex. A person is recorded ONLY when a capitalized
# name token appears immediately after one of these markers in source text.
ROLE_MARKERS = [
    r"Dr\.?", r"Doctor", r"Professor", r"Prof\.?",
    r"journalist", r"reporter", r"correspondent", r"editor", r"anchor",
    r"nurse", r"medic", r"paramedic",
    r"teacher", r"student",
    r"aid worker", r"humanitarian", r"volunteer",
    r"commander", r"general", r"colonel", r"captain",
    r"president", r"prime minister", r"minister", r"leader", r"official",
    r"child", r"boy", r"girl", r"teenager",
    r"doctor", r"physician",
]
_NAME_RE = re.compile(
    r"\b(" + "|".join(ROLE_MARKERS) + r")\s+([A-Z][\w'\u00C0-\u017F]+(?:\s+[A-Z][\w'\u00C0-\u017F]+){0,3})"
)

# Non-person tokens the regex can capture (countries, institutions, generic nouns).
# Rejected during Pass 2 to avoid false positives.
NON_PERSON_TOKENS = {
    "hungary", "ukraine", "gaza", "sudan", "iran", "israel", "yemen", "russia",
    "palestine", "lebanon", "syria", "iraq", "afghanistan", "dail", "parliament",
    "government", "the", "a", "an", "his", "her", "their", "was", "were", "is",
    "president", "minister", "leader", "doctor", "journalist", "child", "commander",
    "about", "lebanese", "israeli", "an", "al", "el", "abu", "bin", "ben", "de",
    "israel", "iran", "gaza", "sudan", "yemen", "palestinian", "houthis",
}

# Conflict/country terms an article MUST contain to be in-scope (Pass 1 country gate).
COUNTRY_KEYWORDS = [
    "gaza", "rafah", "khan younis", "sudan", "khartoum", "darfur", "iran",
    "israel", "yemen", "sanaa", "palestine", "west bank", "lebanon", "idf",
    "hamas", "houthis", "houthi", "idf", "gaza strip",
]


class GuardianAdapter(BaseAdapter):
    source_type = "guardian"

    def fetch(self) -> AdapterResult:
        res = AdapterResult()
        key = os.environ.get("GUARDIAN_API_KEY")
        if not key:
            res.errors.append("GUARDIAN_API_KEY not set — skipping Guardian source.")
            return res

        role_kw = [k.lower() for k in self.cfg.get("role_keywords", [])]
        max_pages = int(self.cfg.get("max_pages", 3))
        page_size = int(self.cfg.get("page_size", 20))

        # ---- Pass 1: paginated discovery + relevance gate ----
        relevant_articles = []
        tags = self.cfg.get("tags")
        tag_batches = [tags[i:i + 4] for i in range(0, len(tags), 4)] if tags else [None]
        for tag_batch in tag_batches:
            for page in range(1, max_pages + 1):
                params = {
                    "api-key": key,
                    "order-by": self.cfg.get("order_by", "newest"),
                    "page-size": page_size,
                    "page": page,
                    "show-fields": "headline,byline,trailText,body,thumbnail",
                    "show-tags": "keyword",
                }
                if tag_batch:
                    params["tag"] = ",".join(tag_batch)
                else:
                    params["q"] = self.cfg.get("query", "")
                if self.cfg.get("section"):
                    params["section"] = self.cfg["section"]
                if self.cfg.get("pillar"):
                    params["pillar"] = self.cfg["pillar"]
                url = f"https://content.guardianapis.com/search?{parse.urlencode(params)}"
                try:
                    data = self._get_json(url)
                except Exception as e:  # noqa: BLE001
                    res.errors.append(f"Guardian API batch error: {e}")
                    break
                results = data.get("response", {}).get("results", [])
                if not results:
                    break
                country_kw = [k.lower() for k in self.cfg.get("country_keywords", COUNTRY_KEYWORDS)]
                casualty_kw = ["killed", "dead", "deaths", "death", "massacre",
                               "airstrike", "air strike", "bombed", "buried", "funeral",
                               "slain", "murdered", "mass grave", "civilian deaths"]
                for art in results:
                    text = self._article_text(art)
                    tlow = text.lower()
                    has_country = any(kw in tlow for kw in country_kw)
                    has_casualty = any(kw in tlow for kw in casualty_kw)
                    if has_country and has_casualty:
                        relevant_articles.append(art)
                        res.raw_meta.setdefault("relevant", []).append(art.get("id"))
                if len(results) < page_size:
                    break
        if not relevant_articles:
            res.errors.append("No conflict-relevant Guardian articles found for current scope.")
            return res

        # ---- Pass 2: named-entity extraction from relevant articles only ----
        for art in relevant_articles:
            people = self._extract_people(art)
            art["_extracted_people"] = people
            res.parsed.append(art)

        res.raw_meta["discovered"] = len(relevant_articles)
        return res

    def _article_text(self, art: dict) -> str:
        f = art.get("fields", {})
        parts = [f.get("headline", ""), f.get("trailText", ""), f.get("body", "")]
        return strip_html(" ".join(p for p in parts if p))

    def _extract_people(self, art: dict) -> list[dict]:
        """Return verified-present person mentions (name + role from source text).
        Only names literally adjacent to a role marker are kept."""
        text = self._article_text(art)
        found = []
        seen = set()
        for m in _NAME_RE.finditer(text):
            marker = m.group(1).lower()
            name = re.sub(r"\s+", " ", m.group(2)).strip()
            if name.lower() in NON_PERSON_TOKENS:
                continue
            key = (name.lower(), marker)
            if key in seen:
                continue
            seen.add(key)
            role = self._map_role(marker)
            found.append({
                "person_name": name,
                "person_role": role,
                "role_marker": marker,
                "source_snippet": text[max(0, m.start() - 40): m.end() + 40],
            })
        return found

    def _map_role(self, marker: str) -> str:
        m = marker.lower()
        mapping = {
            "doctor": "doctor", "physician": "doctor", "dr": "doctor",
            "professor": "teacher", "prof": "teacher", "teacher": "teacher",
            "student": "student",
            "nurse": "nurse", "medic": "medic / paramedic", "paramedic": "medic / paramedic",
            "journalist": "journalist", "reporter": "journalist",
            "correspondent": "journalist", "editor": "journalist", "anchor": "journalist",
            "aid worker": "aid worker", "humanitarian": "aid worker", "volunteer": "aid worker",
            "commander": "military commander", "general": "military commander",
            "colonel": "military commander", "captain": "military commander",
            "president": "political leader", "prime minister": "political leader",
            "minister": "political leader", "leader": "political leader", "official": "political leader",
            "child": "child", "boy": "child", "girl": "child", "teenager": "child",
        }
        return mapping.get(m, "unknown")

    def to_record(self, item: dict) -> dict:
        f = item.get("fields", {})
        body = f.get("body")
        store_full = bool(self.cfg.get("store_full_text", True))
        pub = parse_iso8601(item.get("webPublicationDate"))
        people = item.get("_extracted_people", [])
        return {
            "record_id": f"guardian-{item.get('id')}",
            "source_name": "The Guardian",
            "source_type": "guardian",
            "source_url": item.get("webUrl"),
            "source_date": pub,
            "source_license": "Guardian Content API - internal use; no republication",
            "source_access_method": "api",
            "title": f.get("headline"),
            "subtitle": f.get("trailText"),
            "author": f.get("byline"),
            "publication_date": pub,
            "section": item.get("sectionName"),
            "tags": [t.get("webTitle") for t in item.get("tags", []) if t.get("webTitle")],
            "summary": strip_html(f.get("trailText")),
            "full_text": strip_html(body) if (store_full and body) else None,
            "image_url": f.get("thumbnail"),
            "language": "en",
            "extraction_status": "ok" if people else "partial",
            "confidence_score": 0.9 if people else 0.5,
            "notes": (
                f"Pass-2 extracted {len(people)} named person mention(s) from source text. "
                "Full body stored for internal research use only per Guardian API terms; do not republish."
                if people else
                "Relevant article but no role-adjacent named person extracted; routed to review."
            ),
            "related_articles": [item.get("webUrl")],
            "_people": people,
        }
