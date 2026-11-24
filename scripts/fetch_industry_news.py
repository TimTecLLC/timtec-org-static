#!/usr/bin/env python3
"""Fetch publisher feeds and write the static Industry News page.

One failed feed does not remove items from the feeds that succeeded.
The JSON file and news/index.html are written only when the headlines change.
"""

from __future__ import annotations

import json
import sys
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from news_feeds import FEEDS, NOT_USED, parse_feed
from news_text import date_label, esc, excerpt, isoformat_utc, public_text
from site_chrome import SITE, render_document, write_sitemap

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "industry-news.json"
PAGE_PATH = ROOT / "news" / "index.html"
MAX_ITEMS = 40
USER_AGENT = "TimTecNewsBot/1.0 (+https://www.timtec.org/news/; headline excerpts only)"


def fetch_bytes(url: str, timeout: int = 25) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read()
        content_type = (response.headers.get("content-type") or "").lower()
    if "html" in content_type and not body.lstrip().startswith(b"<"):
        raise ValueError(f"HTML content type from {url}")
    return body


def load_previous() -> dict:
    if not DATA_PATH.exists():
        return {"items": [], "feeds": []}
    try:
        return json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"items": [], "feeds": []}


def build_payload(previous: dict, fetcher=fetch_bytes, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    collected = []
    reports = []
    failed_ids = set()
    for feed in FEEDS:
        report = {"id": feed["id"], "name": feed["name"], "url": feed["url"], "ok": False, "items": 0, "error": ""}
        try:
            raw = fetcher(feed["url"])
            parsed = parse_feed(raw)
        except Exception as exc:  # one bad feed must not stop the others
            report["error"] = str(exc).splitlines()[0][:240]
            reports.append(report)
            failed_ids.add(feed["id"])
            print(f"feed failed: {feed['name']}: {report['error']}", file=sys.stderr)
            continue
        report["ok"] = True
        report["items"] = len(parsed)
        reports.append(report)
        for entry in parsed:
            published = entry["published"]
            collected.append(
                {
                    "feed_id": feed["id"],
                    "source": feed["name"],
                    "title": public_text(entry["title"]),
                    "url": entry["url"],
                    "published": isoformat_utc(published),
                    "excerpt": public_text(excerpt(entry["summary"])),
                    "_stamp": published.timestamp() if published else 0,
                }
            )
    for old in previous.get("items") or []:
        if old.get("feed_id") in failed_ids and old.get("url") and old.get("title"):
            published = old.get("published") or ""
            stamp = 0
            if published:
                try:
                    stamp = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
                except ValueError:
                    stamp = 0
            collected.append(
                {
                    "feed_id": old.get("feed_id") or "",
                    "source": old.get("source") or "",
                    "title": old.get("title") or "",
                    "url": old.get("url") or "",
                    "published": published,
                    "excerpt": old.get("excerpt") or "",
                    "_stamp": stamp,
                }
            )
    collected.sort(key=lambda item: (-item["_stamp"], item["url"]))
    deduped = []
    seen = set()
    for item in collected:
        if item["url"] in seen or not item["title"]:
            continue
        seen.add(item["url"])
        deduped.append({key: item[key] for key in ("feed_id", "source", "title", "url", "published", "excerpt")})
        if len(deduped) >= MAX_ITEMS:
            break
    if not deduped and not any(report["ok"] for report in reports):
        raise RuntimeError("every feed failed and there are no previous headlines")
    return {
        "updated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "max_items": MAX_ITEMS,
        "feeds": reports,
        "not_used": [dict(item) for item in NOT_USED],
        "items": deduped,
    }


def semantic(payload: dict) -> str:
    slim = {
        "feeds": payload.get("feeds") or [],
        "items": payload.get("items") or [],
        "not_used": payload.get("not_used") or [],
    }
    return json.dumps(slim, ensure_ascii=False, sort_keys=True)


def render_industry_page(payload: dict) -> str:
    items = payload.get("items") or []
    cards = []
    list_items = []
    for index, item in enumerate(items, start=1):
        title = esc(item["title"])
        url = esc(item["url"])
        source = esc(item["source"])
        label = date_label(item.get("published") or "")
        when = esc(label)
        iso = esc((item.get("published") or "")[:10])
        blurb = esc(item.get("excerpt") or "")
        meta = f"<span>{source}</span>"
        if label:
            meta += f' · <time datetime="{iso}">{when}</time>'
        paragraph = f"\n              <p>{blurb}</p>" if blurb else ""
        cards.append(
            f"""            <article class="card news-item">
              <h2><a href="{url}" rel="noopener nofollow" target="_blank">{title}</a></h2>
              <p class="news-meta">{meta}</p>{paragraph}
            </article>"""
        )
        list_items.append(
            {
                "@type": "ListItem",
                "position": index,
                "name": item["title"],
                "url": item["url"],
            }
        )
    if cards:
        listing = "\n".join(cards)
    else:
        listing = '            <article class="card news-item"><h2>No headlines yet</h2><p>Publisher feeds have not returned any items.</p></article>'
    sources = []
    for feed in FEEDS:
        if any(item.get("feed_id") == feed["id"] for item in items):
            sources.append(feed["name"])
    source_line = ""
    if sources:
        source_line = f'\n          <p class="news-meta">Sources in this list: {esc(", ".join(sources))}.</p>'
    main = f"""      <section class="page-hero">
        <div class="wrap prose">
          <p class="kicker">News</p>
          <h1>Industry News</h1>
          <p class="lede">Headlines from chemistry, chemical biology, and drug-discovery publishers. Each link opens the original article.</p>
          <p class="news-disclaimer">Headlines link to their publishers.</p>
          <p class="news-switch"><a class="pill" href="../news/" aria-current="page">Industry News</a> <a class="pill" href="../news/cited-in-research/">Cited in Research</a></p>
        </div>
      </section>
      <section class="section">
        <div class="wrap">
          <div class="news-list">
{listing}
          </div>{source_line}
        </div>
      </section>"""
    graph = [
        {
            "@type": "CollectionPage",
            "@id": f"{SITE}/news/#webpage",
            "url": f"{SITE}/news/",
            "name": "Industry News",
            "description": "Headlines from chemistry, chemical biology, and drug-discovery publishers. Each link opens the original article.",
            "isPartOf": {"@id": f"{SITE}/#website"},
            "publisher": {"@id": f"{SITE}/#organization"},
            "mainEntity": {
                "@type": "ItemList",
                "numberOfItems": len(list_items),
                "itemListElement": list_items,
            },
        }
    ]
    return render_document(
        depth=1,
        title="Industry News | TimTec LLC",
        description="Headlines from chemistry, chemical biology, and drug-discovery publishers. Each link opens the original article.",
        keywords="TimTec, industry news, chemistry, chemical biology, drug discovery, Fierce Biotech, Nature, ScienceDaily",
        canonical_path="/news/",
        graph=graph,
        main_html=main,
        current="industry",
    )


def write_outputs(payload: dict, today: str) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    PAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    html = render_industry_page(payload)
    if "timtec.net" in html.lower():
        raise RuntimeError("industry page included a timtec.net URL")
    PAGE_PATH.write_text(html, encoding="utf-8")
    write_sitemap([(f"{SITE}/news/", today)], drop_exact=f"{SITE}/news/")


def main() -> int:
    previous = load_previous()
    try:
        payload = build_payload(previous)
    except Exception:
        traceback.print_exc()
        return 1
    if semantic(payload) == semantic(previous):
        print("industry news unchanged")
        if not PAGE_PATH.exists():
            today = payload["updated"][:10]
            write_outputs(payload, today)
            print(f"wrote missing page with {len(payload['items'])} headlines")
        return 0
    today = payload["updated"][:10]
    write_outputs(payload, today)
    print(f"updated industry news: {len(payload['items'])} headlines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
