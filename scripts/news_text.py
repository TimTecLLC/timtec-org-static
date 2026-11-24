"""Text helpers for TimTec news pages. Standard library only."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

EXCERPT_LIMIT = 200
MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)

TIMTEC_RE = re.compile(r"(?i)(?<![A-Za-z])Tim[\s-]?Tec(?![A-Za-z])")
TAG_RE = re.compile(r"(?is)<[^>]+>")
SCRIPT_RE = re.compile(r"(?is)<(script|style)\b[^>]*>.*?</\1>")
TIMTEC_NET_URL_RE = re.compile(r"(?i)\bhttps?://(?:www\.)?timtec\.net\S*")
TIMTEC_NET_HOST_RE = re.compile(r"(?i)\b(?:www\.)?timtec\.net\b")

DATE_FORMATS = (
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d",
    "%b %d, %Y %I:%M%p",
    "%b %d, %Y %I:%M %p",
    "%d %b %Y",
    "%B %d, %Y",
)


def strip_html(value: str) -> str:
    if not value:
        return ""
    text = SCRIPT_RE.sub(" ", value)
    text = TAG_RE.sub(" ", text)
    text = html.unescape(text)
    text = text.replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def excerpt(value: str, limit: int = EXCERPT_LIMIT) -> str:
    text = strip_html(value)
    if len(text) <= limit:
        return text
    ellipsis = "…"
    budget = limit - len(ellipsis)
    chunk = text[:budget]
    if " " in chunk:
        word = chunk.rsplit(" ", 1)[0]
        if len(word) >= int(budget * 0.6):
            chunk = word
    chunk = chunk.rstrip(" .,;:-–—")
    if not chunk:
        chunk = text[:budget].rstrip()
    result = chunk + ellipsis
    return result[:limit]


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    raw = re.sub(r"(?i)(\d)\s*(am|pm)\b", r"\1 \2", raw)
    try:
        parsed = parsedate_to_datetime(raw)
    except (TypeError, ValueError, IndexError, OverflowError):
        parsed = None
    if parsed is not None:
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    cleaned = raw.replace("Z", "+0000") if raw.endswith("Z") else raw
    for fmt in DATE_FORMATS:
        try:
            parsed = datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    return None


def isoformat_utc(value: datetime | None) -> str:
    if value is None:
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def date_label(iso_value: str) -> str:
    if not iso_value or len(iso_value) < 10:
        return ""
    try:
        year = int(iso_value[0:4])
        month = int(iso_value[5:7])
        day = int(iso_value[8:10])
    except ValueError:
        return ""
    if not 1 <= month <= 12:
        return ""
    return f"{day} {MONTHS[month - 1]} {year}"


def canonical_url(url: str) -> str:
    if not url:
        return ""
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in ("http", "https") or not parts.netloc:
        return ""
    query = [
        (key, val)
        for key, val in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in {"fbclid", "gclid"} and not key.lower().startswith("utm_")
    ]
    query.sort()
    path = parts.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def public_text(value: str) -> str:
    """Public copy uses www.timtec.org. A timtec.net host is not linked or shown."""
    if not value:
        return ""
    text = TIMTEC_NET_URL_RE.sub("", value)
    text = TIMTEC_NET_HOST_RE.sub("TimTec", text)
    return re.sub(r"\s+", " ", text).strip()


def context_snippet(value: str, radius: int = 160, limit: int = 400) -> str:
    text = strip_html(value)
    match = TIMTEC_RE.search(text)
    if not match:
        return ""
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    chunk = text[start:end].strip()
    if start > 0:
        chunk = "…" + chunk
    if end < len(text):
        chunk = chunk + "…"
    if len(chunk) > limit:
        chunk = chunk[: limit - 1].rstrip() + "…"
    return chunk


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)
