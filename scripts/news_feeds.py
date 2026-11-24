"""RSS and Atom parsing for the industry news page."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime

from news_text import canonical_url, parse_datetime, strip_html

# Feeds checked on 2026-11-24. Each URL returned a feed document with items.
# C&EN (cen.acs.org) is not listed: the site no longer publishes an RSS or Atom URL.
# ScienceDaily chemistry, organic chemistry, and biochemistry URLs return XML, but the
# items are general physics and space stories, so those URLs are not used.
FEEDS = (
    {
        "id": "fierce-biotech",
        "name": "Fierce Biotech",
        "url": "https://www.fiercebiotech.com/rss/xml",
    },
    {
        "id": "nature-news",
        "name": "Nature",
        "url": "https://www.nature.com/latest-news.rss",
    },
    {
        "id": "nature-chemical-biology",
        "name": "Nature Chemical Biology",
        "url": "https://www.nature.com/nchembio.rss",
    },
    {
        "id": "nature-chemistry",
        "name": "Nature (Chemistry)",
        "url": "https://www.nature.com/subjects/chemistry.rss",
    },
    {
        "id": "nature-biochemistry",
        "name": "Nature (Biochemistry)",
        "url": "https://www.nature.com/subjects/biochemistry.rss",
    },
    {
        "id": "sciencedaily-pharmacology",
        "name": "ScienceDaily",
        "url": "https://www.sciencedaily.com/rss/health_medicine/pharmacology.xml",
    },
)

NOT_USED = (
    {
        "name": "C&EN",
        "reason": "No checked cen.acs.org or pubs.acs.org URL returned RSS or Atom XML.",
    },
    {
        "name": "ScienceDaily chemistry, organic chemistry, and biochemistry",
        "reason": "The XML is valid, but the items are not chemistry or biochemistry headlines. ScienceDaily pharmacology is used instead.",
    },
)

FEED_ROOTS = {"rss", "rdf", "feed"}
SUMMARY_NAMES = ("description", "summary")
BODY_NAMES = ("encoded", "content")


def local_name(tag: str) -> str:
    if not tag:
        return ""
    return tag.rsplit("}", 1)[-1].lower()


def element_text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def parse_feed(raw: bytes) -> list[dict]:
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    head = raw.lstrip()[:300].lower()
    if head.startswith(b"<!doctype html") or head.startswith(b"<html") or head.startswith(b"<?xml") and b"<html" in head[:300]:
        raise ValueError("response is HTML, not a feed")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError(f"invalid XML: {exc}") from exc
    root_name = local_name(root.tag)
    if root_name not in FEED_ROOTS:
        raise ValueError(f"unexpected feed root <{root_name}>")
    items = []
    for el in root.iter():
        if local_name(el.tag) not in {"item", "entry"}:
            continue
        parsed = parse_entry(el)
        if parsed:
            items.append(parsed)
    if not items:
        raise ValueError("feed XML has no items")
    return items


def parse_entry(el: ET.Element) -> dict | None:
    title = ""
    summary = ""
    body = ""
    published: datetime | None = None
    link = ""
    for child in list(el):
        name = local_name(child.tag)
        if name == "title" and not title:
            title = element_text(child)
        elif name in SUMMARY_NAMES and not summary:
            summary = element_text(child)
        elif name in BODY_NAMES and not body:
            body = element_text(child)
        elif name in {"pubdate", "published", "updated", "date"} and published is None:
            published = parse_datetime(element_text(child))
        elif name == "link" and not link:
            href = (child.attrib.get("href") or "").strip()
            rel = (child.attrib.get("rel") or "alternate").strip()
            if href and rel in {"alternate", ""}:
                link = href
            elif child.text and child.text.strip().startswith("http"):
                link = child.text.strip()
    url = canonical_url(link)
    title = strip_html(title)
    if not title or not url:
        return None
    raw_summary = summary if strip_html(summary) else body
    return {
        "title": title,
        "url": url,
        "published": published,
        "summary": raw_summary or "",
    }
