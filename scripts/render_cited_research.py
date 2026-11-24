#!/usr/bin/env python3
"""Render public Cited in Research pages from published entries only.

Draft and rejected entries stay in data/cited-research.json and are not written
to HTML. Publishing is a human edit: set status to "published" and merge.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from news_text import esc, excerpt, public_text
from site_chrome import SITE, prefix, render_document, write_sitemap

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cited-research.json"
HUB_DIR = ROOT / "news" / "cited-in-research"

COLLECTION_PAGES = {
    "NPL-800": "screening-collections/npl-800/",
    "NDL-3040": "screening-collections/ndl-3040/",
    "FL-500": "screening-collections/fl-500/",
    "ApexScreen": "screening-collections/apexscreen/",
    "ActiGlobe-50K": "screening-collections/actiglobe-50k/",
    "ActiProbe-10K": "screening-collections/actiprobe-10k/",
    "FBL": "screening-collections/fbl/",
    "MS-10000": "screening-collections/ms-10000/",
    "ActiTarg-G": "screening-collections/actitarg-g/",
    "ActiTarg-K": "screening-collections/actitarg-k/",
    "ActiTarg-P": "screening-collections/actitarg-p/",
    "ActiTarg-S": "screening-collections/actitarg-s/",
    "ActiTarg-I": "screening-collections/actitarg-i/",
    "ActiTarg-N": "screening-collections/actitarg-n/",
    "ActiTarg-H": "screening-collections/actitarg-h/",
    "ActiTarg-CNS": "screening-collections/actitarg-cns/",
    "MAC-15000": "screening-collections/mac-15000/",
}

MCL_RE = re.compile(r"(?i)^MCL[-\s]?5000$")


def load_data() -> dict:
    if not DATA_PATH.exists():
        return {"entries": []}
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def published_entries(data: dict) -> list[dict]:
    entries = []
    for entry in data.get("entries") or []:
        if str(entry.get("status") or "").lower() != "published":
            continue
        if not (entry.get("title") and (entry.get("doi_url") or entry.get("doi"))):
            continue
        entries.append(entry)
    entries.sort(key=lambda item: (-int(item.get("year") or 0), item.get("title") or ""))
    return entries


def slug_for(entry: dict) -> str:
    raw = entry.get("doi") or entry.get("id") or entry.get("title") or "paper"
    slug = re.sub(r"[^a-z0-9]+", "-", str(raw).lower()).strip("-")
    return slug[:90] or "paper"


def entry_slug(entry: dict) -> str:
    return entry.get("_slug") or slug_for(entry)


def doi_url(entry: dict) -> str:
    explicit = (entry.get("doi_url") or "").strip()
    if explicit.startswith("https://doi.org/"):
        return explicit
    doi = (entry.get("doi") or "").strip()
    doi = re.sub(r"(?i)^https?://(dx\.)?doi\.org/", "", doi)
    if not doi:
        return explicit
    return "https://doi.org/" + doi


def author_names(display: str) -> list[str]:
    names = []
    for part in (display or "").split(";"):
        name = part.strip().strip(".")
        if not name or name.lower() == "et al":
            continue
        names.append(part.strip())
    return names


def collection_html(names: list[str], depth: int) -> str:
    pre = prefix(depth)
    linked = []
    notes = []
    for name in names or []:
        clean = str(name).strip()
        if not clean:
            continue
        if MCL_RE.match(clean):
            notes.append(
                f'<a href="{pre}screening-collections/mac-15000/">MAC-15000</a> is the commercial macrocycle screening collection.'
            )
            continue
        path = COLLECTION_PAGES.get(clean)
        if path:
            linked.append(f'<a href="{pre}{esc(path)}">{esc(clean)}</a>')
        else:
            linked.append(esc(clean))
    sentences = []
    if linked:
        sentences.append("TimTec collection: " + ", ".join(linked) + ".")
    sentences.extend(notes)
    if not sentences:
        sentences.append("The paper does not state a TimTec collection name.")
    return " ".join(sentences)


def meta_description(entry: dict) -> str:
    summary = public_text(entry.get("summary") or "")
    if not summary:
        summary = f"Citation for a paper that used a TimTec library: {entry.get('title')}"
    text = excerpt(summary, 160)
    return esc(text)


def switch(depth: int, cited_current: bool) -> str:
    pre = prefix(depth)
    cited_attr = ' aria-current="page"' if cited_current else ""
    return (
        f'<p class="news-switch"><a class="pill" href="{pre}news/">Industry News</a> '
        f'<a class="pill" href="{pre}news/cited-in-research/"{cited_attr}>Cited in Research</a></p>'
    )


def render_hub(entries: list[dict]) -> str:
    cards = []
    list_items = []
    for index, entry in enumerate(entries, start=1):
        slug = entry_slug(entry)
        href = esc(slug + "/")
        title = esc(public_text(entry["title"]))
        authors = esc(public_text(entry.get("author_display") or ""))
        journal = esc(public_text(entry.get("journal") or ""))
        year = esc(entry.get("year") or "")
        bits = [bit for bit in (authors, journal, year) if bit]
        meta = " · ".join(bits)
        summary = esc(public_text(entry.get("summary") or ""))
        summary_html = f"\n              <p>{summary}</p>" if summary else ""
        cards.append(
            f"""            <article class="card news-item">
              <h2><a href="{href}">{title}</a></h2>
              <p class="news-meta">{meta}</p>{summary_html}
            </article>"""
        )
        list_items.append(
            {
                "@type": "ListItem",
                "position": index,
                "name": public_text(entry["title"]),
                "url": f"{SITE}/news/cited-in-research/{entry_slug(entry)}/",
            }
        )
    if cards:
        listing = "\n".join(cards)
        lede = "Peer-reviewed papers that used TimTec compounds or screening libraries. Each page has the citation, the DOI, and the collection named in the paper."
    else:
        listing = """            <article class="card news-item">
              <h2>No papers published here yet</h2>
              <p>TimTec adds a paper to this page after review. Drafts are not listed.</p>
            </article>"""
        lede = "Peer-reviewed papers that used TimTec compounds or screening libraries will be listed here after TimTec review."
    main = f"""      <section class="page-hero">
        <div class="wrap prose">
          <p class="kicker">News</p>
          <h1>Cited in Research</h1>
          <p class="lede">{esc(lede)}</p>
          {switch(2, True)}
        </div>
      </section>
      <section class="section">
        <div class="wrap">
          <div class="news-list">
{listing}
          </div>
          <p class="news-disclaimer">These pages cite the publishers. They are not the papers themselves.</p>
        </div>
      </section>"""
    graph = [
        {
            "@type": "CollectionPage",
            "@id": f"{SITE}/news/cited-in-research/#webpage",
            "url": f"{SITE}/news/cited-in-research/",
            "name": "Cited in Research",
            "description": lede,
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
        depth=2,
        title="Cited in Research | TimTec LLC",
        description=esc(excerpt(lede, 160)),
        keywords="TimTec, cited in research, screening library, peer-reviewed papers",
        canonical_path="/news/cited-in-research/",
        graph=graph,
        main_html=main,
        current="cited",
    )


def render_post(entry: dict) -> str:
    slug = entry_slug(entry)
    title = public_text(entry["title"])
    authors = public_text(entry.get("author_display") or "")
    journal = public_text(entry.get("journal") or "")
    year = str(entry.get("year") or "")
    link = doi_url(entry)
    summary = public_text(entry.get("summary") or "") or "TimTec has not added a summary for this paper yet."
    snippet = public_text(entry.get("snippet") or "")
    collections = entry.get("collections") or []
    if isinstance(collections, str):
        collections = [collections]
    citation_bits = [esc(authors)] if authors else []
    if journal:
        citation_bits.append(f"<em>{esc(journal)}</em>")
    if year:
        citation_bits.append(esc(year))
    citation = ". ".join(bit.rstrip(".") for bit in citation_bits)
    if citation and not citation.endswith("."):
        citation += "."
    context = ""
    if snippet:
        context = f"""
          <h2>Where the paper mentions TimTec</h2>
          <p class="note">{esc(snippet)}</p>"""
    description = meta_description(entry)
    page_name = title if len(title) <= 150 else title[:149].rstrip() + "…"
    authors_schema = [{"@type": "Person", "name": name} for name in author_names(authors)]
    article = {
        "@type": "ScholarlyArticle",
        "@id": link,
        "headline": title,
        "name": title,
        "datePublished": year or None,
        "url": link,
        "sameAs": link,
        "description": public_text(entry.get("summary") or title),
        "isPartOf": {"@type": "Periodical", "name": journal} if journal else None,
    }
    if authors_schema:
        article["author"] = authors_schema
    if entry.get("doi"):
        article["identifier"] = {"@type": "PropertyValue", "propertyID": "DOI", "value": entry["doi"]}
    article = {key: value for key, value in article.items() if value not in (None, "", [])}
    page = {
        "@type": "WebPage",
        "@id": f"{SITE}/news/cited-in-research/{slug}/#webpage",
        "url": f"{SITE}/news/cited-in-research/{slug}/",
        "name": page_name,
        "description": public_text(entry.get("summary") or title),
        "isPartOf": {"@id": f"{SITE}/#website"},
        "publisher": {"@id": f"{SITE}/#organization"},
        "about": {"@id": link},
    }
    main = f"""      <section class="page-hero">
        <div class="wrap prose">
          <p class="kicker">Cited in Research</p>
          <h1>{esc(title)}</h1>
          {switch(3, True)}
        </div>
      </section>
      <section class="section">
        <div class="wrap prose">
          <p>{citation}</p>
          <p><a href="{esc(link)}">doi:{esc(entry.get("doi") or link.removeprefix("https://doi.org/"))}</a></p>
          <h2>Summary</h2>
          <p>{esc(summary)}</p>
          <h2>TimTec collection</h2>
          <p>{collection_html(collections, 3)}</p>{context}
          <p><a href="../">All cited papers</a></p>
        </div>
      </section>"""
    return render_document(
        depth=3,
        title=esc(page_name + " | TimTec LLC"),
        description=description,
        keywords=esc(
            "TimTec, "
            + ", ".join(
                [name for name in collections if name and not MCL_RE.match(str(name))]
                + ([journal] if journal else [])
                + ["cited in research"]
            )
        ),
        canonical_path=f"/news/cited-in-research/{slug}/",
        graph=[page, article],
        main_html=main,
        current="cited",
    )


def remove_stale_posts(slugs: set[str]) -> None:
    if not HUB_DIR.exists():
        return
    for child in HUB_DIR.iterdir():
        if child.is_dir() and child.name not in slugs:
            shutil.rmtree(child)


def render_all(today: str | None = None) -> int:
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = load_data()
    entries = published_entries(data)
    slugs = []
    seen = set()
    for entry in entries:
        base = slug_for(entry)
        slug = base
        number = 2
        while slug in seen:
            slug = f"{base}-{number}"
            number += 1
        seen.add(slug)
        entry["_slug"] = slug
        slugs.append(slug)
    HUB_DIR.mkdir(parents=True, exist_ok=True)
    remove_stale_posts(set(slugs))
    hub_html = render_hub(entries)
    (HUB_DIR / "index.html").write_text(hub_html, encoding="utf-8")
    sitemap_entries = [(f"{SITE}/news/cited-in-research/", today)]
    for entry in entries:
        slug = entry["_slug"]
        html = render_post(entry)
        if "timtec.net" in html.lower() or "timtec.net" in hub_html.lower():
            raise RuntimeError("cited page included a timtec.net URL")
        post_dir = HUB_DIR / slug
        post_dir.mkdir(parents=True, exist_ok=True)
        (post_dir / "index.html").write_text(html, encoding="utf-8")
        sitemap_entries.append((f"{SITE}/news/cited-in-research/{slug}/", today))
    write_sitemap(sitemap_entries, drop_prefix=f"{SITE}/news/cited-in-research")
    print(f"rendered {len(entries)} published cited-research pages")
    return len(entries)


def main() -> int:
    render_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
