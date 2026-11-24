#!/usr/bin/env python3
"""Find peer-reviewed TimTec mentions and store them as drafts.

Searches the Europe PMC full-text index for the word TimTec. It does not search
catalog numbers. Every new hit is status "draft". This script never sets
status to "published".
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from news_text import TIMTEC_RE, context_snippet, strip_html

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cited-research.json"
EPMC_QUERY = '(TITLE:"TimTec" OR ABSTRACT:"TimTec" OR BODY:"TimTec") NOT SRC:PPR'
EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
USER_AGENT = "TimTecCitationBot/1.0 (+https://www.timtec.org/news/cited-in-research/; mailto:timtec@timtec.org)"
SKIP_SOURCES = {"PPR", "PAT", "BOOK", "GRANTS"}
REVIEW_STEPS = [
    "Open the pull request, or edit data/cited-research.json on a branch.",
    "For each entry with status draft, read title, author_display, journal, year, doi_url, and snippet.",
    "If the paper did not use TimTec compounds or a TimTec library, set status to rejected.",
    "To publish, set status to published, replace summary with a short neutral summary, and set collections to the TimTec library names stated in the paper.",
    "Merge into main. The render workflow rebuilds /news/cited-in-research/ from entries whose status is published. Drafts stay off the public page.",
]


def entry_keys(entry: dict) -> set[str]:
    keys = set()
    doi = re.sub(r"(?i)^https?://(?:dx\.)?doi\.org/", "", (entry.get("doi") or entry.get("doi_url") or "").strip()).lower()
    if doi:
        keys.add("doi:" + doi)
    pmid = str(entry.get("pmid") or "").strip()
    if pmid and pmid.lower() not in {"none", "null"}:
        keys.add("pmid:" + pmid)
    pmcid = str(entry.get("pmcid") or "").strip().upper()
    if pmcid:
        if not pmcid.startswith("PMC"):
            pmcid = "PMC" + pmcid
        keys.add("pmcid:" + pmcid)
    return keys


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def get_bytes(url: str, accept: str, timeout: int = 120) -> bytes:
    last_error = None
    for attempt in range(3):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 500, 502, 503, 504}:
                raise
        except urllib.error.URLError as exc:
            last_error = exc
        time.sleep(1.5 * (attempt + 1))
    raise last_error


def normalize_epmc(raw: dict) -> dict | None:
    source = str(raw.get("source") or "")
    pub_type = raw.get("pubType") or ""
    if isinstance(pub_type, list):
        pub_type = ", ".join(str(item) for item in pub_type)
    if source.upper() in SKIP_SOURCES or "preprint" in str(pub_type).lower():
        return None
    title = strip_html(raw.get("title") or "")
    if not title:
        return None
    journal = raw.get("journalTitle") or ""
    if not journal and isinstance(raw.get("journalInfo"), dict):
        journal_info = raw["journalInfo"].get("journal") or {}
        if isinstance(journal_info, dict):
            journal = journal_info.get("title") or ""
    try:
        year = int(raw.get("pubYear"))
    except (TypeError, ValueError):
        year = None
    pmid = str(raw.get("pmid") or "").strip()
    return {
        "title": title,
        "author_display": strip_html(raw.get("authorString") or ""),
        "journal": strip_html(journal),
        "year": year,
        "doi": (raw.get("doi") or "").strip(),
        "pmid": pmid,
        "pmcid": (raw.get("pmcid") or "").strip(),
        "source_db": source,
        "pub_type": str(pub_type),
        "abstract": raw.get("abstractText") or "",
        "origin": "Europe PMC",
    }


def draft_from_record(record: dict, full_text: str, today: str) -> dict | None:
    title = record.get("title") or ""
    abstract = record.get("abstract") or ""
    if TIMTEC_RE.search(title):
        match_in = "title"
        snippet = context_snippet(title) or title
    elif TIMTEC_RE.search(abstract):
        match_in = "abstract"
        snippet = context_snippet(abstract)
    elif full_text and TIMTEC_RE.search(full_text):
        match_in = "fulltext"
        snippet = context_snippet(full_text)
    else:
        match_in = "index"
        snippet = (
            "Europe PMC indexed a TimTec mention for this record. "
            "The title, abstract, and open full text did not include a quotable passage. "
            "Read the paper before publishing."
        )
    if not snippet:
        return None
    doi = record.get("doi") or ""
    keys = entry_keys(record)
    if not keys:
        return None
    doi_url = "https://doi.org/" + doi if doi else ""
    return {
        "id": sorted(keys)[0],
        "status": "draft",
        "title": title,
        "author_display": record.get("author_display") or "",
        "journal": record.get("journal") or "",
        "year": record.get("year"),
        "doi": doi,
        "doi_url": doi_url,
        "pmid": record.get("pmid") or "",
        "pmcid": record.get("pmcid") or "",
        "snippet": snippet,
        "match_in": match_in,
        "summary": "",
        "summary_placeholder": "Write a short neutral summary at review time.",
        "collections": [],
        "source": record.get("origin") or "Europe PMC",
        "discovered_at": today,
    }


def new_drafts(records: list[dict], existing: list[dict], full_text_for, today: str) -> list[dict]:
    known = set()
    for entry in existing:
        known.update(entry_keys(entry))
    fresh = []
    seen = set()
    for record in records:
        keys = entry_keys(record)
        if not keys or keys & known or keys & seen:
            continue
        full_text = ""
        if record.get("pmcid") and not (
            TIMTEC_RE.search(record.get("title") or "") or TIMTEC_RE.search(record.get("abstract") or "")
        ):
            full_text = full_text_for(record.get("pmcid") or "") or ""
        draft = draft_from_record(record, full_text, today)
        if not draft or draft["status"] != "draft":
            continue
        fresh.append(draft)
        seen.update(keys)
    return fresh


def search_epmc() -> list[dict]:
    cursor = "*"
    seen_cursors = set()
    records = []
    for _page in range(20):
        if not cursor or cursor in seen_cursors:
            break
        seen_cursors.add(cursor)
        params = urllib.parse.urlencode(
            {
                "query": EPMC_QUERY,
                "format": "json",
                "resultType": "core",
                "pageSize": "25",
                "cursorMark": cursor,
                "synonym": "false",
            }
        )
        payload = json.loads(get_bytes(EPMC_SEARCH + "?" + params, "application/json").decode("utf-8"))
        batch = as_list((payload.get("resultList") or {}).get("result"))
        if not batch:
            break
        print(f"Europe PMC page {_page + 1}: {len(batch)} hits", flush=True)
        for raw in batch:
            record = normalize_epmc(raw)
            if record:
                records.append(record)
        hit_count = int(payload.get("hitCount") or 0)
        cursor = payload.get("nextCursorMark") or ""
        if hit_count and len(records) >= hit_count:
            break
    return records


def fetch_full_text(pmcid: str) -> str:
    pmcid = (pmcid or "").strip().upper()
    if not pmcid:
        return ""
    if not pmcid.startswith("PMC"):
        pmcid = "PMC" + pmcid
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
    try:
        raw = get_bytes(url, "application/xml, text/xml, */*", timeout=45)
    except Exception as exc:
        print(f"full text skipped {pmcid}: {exc}", file=sys.stderr)
        return ""
    try:
        root = ET.fromstring(raw)
        return " ".join(root.itertext())
    except ET.ParseError:
        return strip_html(raw.decode("utf-8", "replace"))


def preload_full_text(records: list[dict]) -> dict[str, str]:
    needed = []
    for record in records:
        pmcid = (record.get("pmcid") or "").upper()
        if not pmcid:
            continue
        if TIMTEC_RE.search(record.get("title") or "") or TIMTEC_RE.search(record.get("abstract") or ""):
            continue
        needed.append(pmcid if pmcid.startswith("PMC") else "PMC" + pmcid)
    texts = {}
    unique = list(dict.fromkeys(needed))
    if not unique:
        return texts
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(fetch_full_text, pmcid): pmcid for pmcid in unique}
        for future in as_completed(futures):
            pmcid = futures[future]
            try:
                texts[pmcid] = future.result()
            except Exception as exc:
                print(f"full text skipped {pmcid}: {exc}", file=sys.stderr)
                texts[pmcid] = ""
    return texts


def search_pubmed(existing_keys: set[str]) -> list[dict]:
    """Optional MEDLINE supplement. A hit is kept only when the title or abstract says TimTec."""
    query = urllib.parse.urlencode(
        {
            "db": "pubmed",
            "term": '"TimTec"',
            "retmode": "json",
            "retmax": "200",
            "tool": "timtec_cited_research",
            "email": "timtec@timtec.org",
        }
    )
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?" + query
    try:
        payload = json.loads(get_bytes(url, "application/json", timeout=40).decode("utf-8"))
    except Exception as exc:
        print(f"PubMed search skipped: {exc}", file=sys.stderr)
        return []
    ids = (payload.get("esearchresult") or {}).get("idlist") or []
    wanted = [pmid for pmid in ids if f"pmid:{pmid}" not in existing_keys]
    if not wanted:
        return []
    time.sleep(0.4)
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + urllib.parse.urlencode(
        {
            "db": "pubmed",
            "id": ",".join(wanted[:100]),
            "retmode": "xml",
            "tool": "timtec_cited_research",
            "email": "timtec@timtec.org",
        }
    )
    try:
        raw = get_bytes(fetch_url, "application/xml, text/xml", timeout=60)
    except Exception as exc:
        print(f"PubMed fetch skipped: {exc}", file=sys.stderr)
        return []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        print(f"PubMed XML skipped: {exc}", file=sys.stderr)
        return []
    records = []
    for article in root.iter("PubmedArticle"):
        pmid = element_text(article.find(".//PMID"))
        title = element_text(article.find(".//ArticleTitle"))
        abstract = " ".join(element_text(node) for node in article.findall(".//AbstractText"))
        if not TIMTEC_RE.search(title) and not TIMTEC_RE.search(abstract):
            continue
        doi = ""
        for node in article.findall(".//ArticleId"):
            if (node.attrib.get("IdType") or "").lower() == "doi" and (node.text or "").strip():
                doi = node.text.strip()
                break
        if doi and f"doi:{doi.lower()}" in existing_keys:
            continue
        authors = []
        for author in article.findall(".//Author"):
            last = element_text(author.find("LastName"))
            initials = element_text(author.find("Initials"))
            if last:
                authors.append((last + " " + initials).strip())
        journal = element_text(article.find(".//Journal/Title"))
        year_text = element_text(article.find(".//PubDate/Year")) or element_text(article.find(".//PubDate/MedlineDate"))
        year_match = re.search(r"\d{4}", year_text or "")
        records.append(
            {
                "title": strip_html(title),
                "author_display": "; ".join(authors),
                "journal": strip_html(journal),
                "year": int(year_match.group(0)) if year_match else None,
                "doi": doi,
                "pmid": pmid,
                "pmcid": "",
                "source_db": "MED",
                "pub_type": "",
                "abstract": abstract,
                "origin": "PubMed",
            }
        )
    return records


def element_text(node) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def build_pr_body(new_entries: list[dict], pending_count: int) -> str:
    lines = [
        "## Cited in Research drafts for review",
        "",
        "These candidates are **drafts**. Merging this pull request does not publish them.",
        "The public page lists an entry only after `status` is `published`.",
        "",
        f"New drafts in this run: **{len(new_entries)}**. Pending drafts in the file: **{pending_count}**.",
        "",
        "### How to review and publish",
        "",
    ]
    for step in REVIEW_STEPS:
        lines.append(f"- {step}")
    lines.extend(
        [
            "",
            "Do not publish from a catalog-number search. Confirm the paper itself names TimTec or a TimTec library.",
            "",
            "### New candidates",
            "",
        ]
    )
    used = len("\n".join(lines))
    shown = 0
    for entry in new_entries:
        block = [
            f"#### {entry.get('title') or 'Untitled'}",
            "",
            f"- Authors: {entry.get('author_display') or 'not listed'}",
            f"- Journal: {entry.get('journal') or 'not listed'}",
            f"- Year: {entry.get('year') or 'not listed'}",
            f"- DOI: {entry.get('doi_url') or 'no DOI on the record'}",
            f"- Matching snippet: {entry.get('snippet') or ''}",
            "",
        ]
        chunk = "\n".join(block)
        if used + len(chunk) > 55000:
            break
        lines.extend(block)
        used += len(chunk)
        shown += 1
    remaining = len(new_entries) - shown
    if remaining:
        lines.append(
            f"{remaining} more new drafts are in `data/cited-research.json` "
            "(status `draft`), each with title, authors, journal, year, doi_url, and snippet."
        )
        lines.append("")
    lines.append("Publishing still requires a person to set `status` to `published` and merge that change.")
    return "\n".join(lines).strip() + "\n"


def load_store() -> dict:
    if not DATA_PATH.exists():
        return {"review": {"steps": REVIEW_STEPS}, "entries": []}
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr-body", default="", help="Write the review pull-request body to this path")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if "ST0" in EPMC_QUERY or re.search(r"\bST\d", EPMC_QUERY):
        print("refusing a catalog-number query", file=sys.stderr)
        return 1
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    store = load_store()
    entries = list(store.get("entries") or [])
    try:
        records = search_epmc()
    except Exception as exc:
        print(f"Europe PMC search failed: {exc}", file=sys.stderr)
        return 1
    print(f"Europe PMC records: {len(records)}")
    texts = preload_full_text(records)

    def full_text_for(pmcid: str) -> str:
        key = (pmcid or "").upper()
        if key and not key.startswith("PMC"):
            key = "PMC" + key
        return texts.get(key, "")

    found = new_drafts(records, entries, full_text_for, today)
    known = set()
    for entry in entries + found:
        known.update(entry_keys(entry))
    try:
        pubmed_records = search_pubmed(known)
    except Exception as exc:
        print(f"PubMed supplement skipped: {exc}", file=sys.stderr)
        pubmed_records = []
    found.extend(new_drafts(pubmed_records, entries + found, lambda _pmcid: "", today))
    print(f"new drafts: {len(found)}")
    if not found:
        if args.pr_body:
            pending = sum(1 for entry in entries if str(entry.get("status")).lower() == "draft")
            Path(args.pr_body).write_text(build_pr_body([], pending), encoding="utf-8")
        return 0
    entries.extend(found)
    store["entries"] = entries
    store.setdefault("review", {"steps": REVIEW_STEPS})
    if not args.dry_run:
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        DATA_PATH.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending = sum(1 for entry in entries if str(entry.get("status")).lower() == "draft")
    if args.pr_body:
        Path(args.pr_body).write_text(build_pr_body(found, pending), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
