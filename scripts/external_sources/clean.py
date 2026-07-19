"""
Text + date cleaning utilities. Stdlib-only.
- strip_html: remove tags, decode common entities
- normalize_ws: collapse whitespace
- parse_iso8601 / parse_rfc822: normalize dates to ISO-8601 (UTC)
"""
import re
import html
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return normalize_ws(text).strip()


def normalize_ws(text: str) -> str:
    if not text:
        return ""
    return _WS_RE.sub(" ", text).strip()


def parse_iso8601(value: str) -> str | None:
    """Accept ISO-8601 (with/without tz). Return ISO-8601 UTC or None."""
    if not value:
        return None
    value = value.strip()
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def parse_rfc822(value: str) -> str | None:
    """Parse RSS pubDate (RFC-822) to ISO-8601 UTC."""
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")
