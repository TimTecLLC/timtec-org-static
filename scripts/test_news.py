#!/usr/bin/env python3
"""Unit tests for the news feeds and cited-research pages. No network."""

from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from discover_citations import EPMC_QUERY, build_pr_body, draft_from_record, entry_keys, new_drafts
from fetch_industry_news import build_payload, render_industry_page
from news_feeds import parse_feed
from news_text import canonical_url, context_snippet, excerpt, parse_datetime, public_text, strip_html
from render_cited_research import collection_html, published_entries, render_hub, render_post, slug_for
from site_chrome import upsert_sitemap

FIERCE = b"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>Fierce Biotech</title>
    <item>
      <title><a href="/example">DiaMedica shares signs that a drug extends pregnancy</a></title>
      <link>https://www.fiercebiotech.com/biotech/example?utm_source=rss</link>
      <description>DiaMedica Therapeutics has shared phase 2 results in a short excerpt that should remain under the limit.</description>
      <pubDate>Nov 24, 2026 9:34am</pubDate>
    </item>
  </channel>
</rss>
"""

NATURE = b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns="http://purl.org/rss/1.0/"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel><title>Nature Chemical Biology</title></channel>
  <item>
    <title>EPAC control goes regional</title>
    <link>https://www.nature.com/articles/s41589-026-02368-x</link>
    <dc:date>2026-11-24</dc:date>
    <content:encoded><![CDATA[<p>Nature Chemical Biology, Published online: 24 November 2026.</p>]]></content:encoded>
  </item>
</rdf:RDF>
"""

ATOM = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Example</title>
  <entry>
    <title>Atom headline</title>
    <link rel="alternate" href="https://example.org/atom-story"/>
    <updated>2026-11-24T12:00:00Z</updated>
    <summary>A short atom summary.</summary>
  </entry>
</feed>
"""


class TextTests(unittest.TestCase):
    def test_excerpt_strips_html_and_caps_length(self):
        raw = "<p>Hello <b>world</b> &amp; friends. " + ("word " * 80) + "</p><script>alert(1)</script>"
        text = excerpt(raw)
        self.assertNotIn("<", text)
        self.assertNotIn("alert", text)
        self.assertLessEqual(len(text), 200)
        self.assertTrue(text.endswith("…"))
        self.assertIn("Hello world & friends.", text)

    def test_public_text_drops_timtec_net(self):
        cleaned = public_text("See https://www.timtec.net/old and www.timtec.net for the library.")
        self.assertNotIn("timtec.net", cleaned.lower())
        self.assertIn("TimTec", cleaned)

    def test_snippet_has_context(self):
        snippet = context_snippet("Before the screen, TimTec supplied the library, and the assay continued after that sentence.")
        self.assertIn("TimTec", snippet)
        self.assertLessEqual(len(snippet), 400)

    def test_date_without_timezone(self):
        parsed = parse_datetime("Nov 24, 2026 9:34am")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.astimezone(timezone.utc).date().isoformat(), "2026-11-24")


class FeedTests(unittest.TestCase):
    def test_parse_rss_atom_and_rdf(self):
        fierce = parse_feed(FIERCE)[0]
        self.assertEqual(fierce["title"], "DiaMedica shares signs that a drug extends pregnancy")
        self.assertEqual(canonical_url(fierce["url"]), "https://www.fiercebiotech.com/biotech/example")
        nature = parse_feed(NATURE)[0]
        self.assertEqual(nature["title"], "EPAC control goes regional")
        self.assertIn("Nature Chemical Biology", strip_html(nature["summary"]))
        atom = parse_feed(ATOM)[0]
        self.assertEqual(atom["url"], "https://example.org/atom-story")

    def test_html_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_feed(b"<!DOCTYPE html><html><title>Not a feed</title></html>")

    def test_one_failed_feed_keeps_the_other_and_previous_items(self):
        previous = {
            "items": [
                {
                    "feed_id": "fierce-biotech",
                    "source": "Fierce Biotech",
                    "title": "Older Fierce headline",
                    "url": "https://www.fiercebiotech.com/biotech/older",
                    "published": "2026-11-23T00:00:00Z",
                    "excerpt": "Kept when the feed fails.",
                }
            ]
        }

        def fetcher(url: str) -> bytes:
            if "fiercebiotech" in url:
                raise RuntimeError("timeout")
            if "nchembio" in url:
                return NATURE
            raise RuntimeError("down")

        payload = build_payload(previous, fetcher=fetcher, now=datetime(2026, 11, 24, tzinfo=timezone.utc))
        urls = [item["url"] for item in payload["items"]]
        self.assertIn("https://www.nature.com/articles/s41589-026-02368-x", urls)
        self.assertIn("https://www.fiercebiotech.com/biotech/older", urls)
        failed = [feed for feed in payload["feeds"] if feed["id"] == "nature-chemistry"]
        self.assertTrue(failed)
        self.assertFalse(failed[0]["ok"])

    def test_industry_page_is_static_and_not_an_article(self):
        payload = build_payload({"items": []}, fetcher=lambda url: FIERCE if "fiercebiotech" in url else NATURE)
        html = render_industry_page(payload)
        self.assertIn('rel="noopener nofollow"', html)
        self.assertIn('target="_blank"', html)
        self.assertIn('href="https://www.timtec.org/news/"', html)
        self.assertIn("Headlines link to their publishers.", html)
        self.assertIn('"@type": "CollectionPage"', html)
        self.assertIn('"@type": "ItemList"', html)
        self.assertNotIn("NewsArticle", html)
        self.assertNotIn("ScholarlyArticle", html)
        self.assertNotIn('"@type": "Article"', html)
        listing = html.split('<div class="news-list">', 1)[1].split("</div>", 1)[0]
        self.assertNotIn("<img", listing)
        self.assertNotIn("timtec.net", html.lower())
        for item in payload["items"]:
            self.assertLessEqual(len(item["excerpt"]), 200)


class CitedTests(unittest.TestCase):
    def test_query_is_the_name_not_a_catalog_number(self):
        self.assertIn("TimTec", EPMC_QUERY)
        self.assertNotIn("ST0", EPMC_QUERY)
        self.assertNotRegex(EPMC_QUERY, r"ST\d")

    def test_drafts_are_not_published_and_known_dois_are_skipped(self):
        existing = [{"doi": "10.1000/example", "status": "published", "title": "Already listed"}]
        record = {
            "title": "A screen that used TimTec libraries",
            "author_display": "Ada Example",
            "journal": "J. Test.",
            "year": 2024,
            "doi": "10.1000/new",
            "pmid": "1",
            "pmcid": "",
            "abstract": "The assay used a TimTec screening library.",
            "origin": "Europe PMC",
        }
        duplicate = dict(record, doi="10.1000/example", pmid="2")
        drafts = new_drafts([record, duplicate], existing, lambda _pmcid: "", "2026-11-24")
        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0]["status"], "draft")
        self.assertEqual(drafts[0]["summary"], "")
        self.assertIn("TimTec", drafts[0]["snippet"])
        self.assertTrue(entry_keys(drafts[0]) & entry_keys({"doi": "10.1000/new"}))
        self.assertNotIn("ST056388", drafts[0]["snippet"])

    def test_index_only_hit_stays_a_draft(self):
        draft = draft_from_record(
            {
                "title": "No name in the title",
                "author_display": "",
                "journal": "J. Test.",
                "year": 2020,
                "doi": "10.1000/closed",
                "pmid": "",
                "pmcid": "PMC1",
                "abstract": "Nothing here.",
                "origin": "Europe PMC",
            },
            "",
            "2026-11-24",
        )
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(draft["match_in"], "index")

    def test_public_pages_skip_drafts(self):
        data = {
            "entries": [
                {
                    "status": "draft",
                    "title": "Secret draft",
                    "doi": "10.1000/draft",
                    "doi_url": "https://doi.org/10.1000/draft",
                    "year": 2024,
                    "author_display": "A. Researcher",
                    "journal": "J. Draft",
                    "summary": "",
                    "snippet": "TimTec appears in this draft snippet.",
                    "collections": ["NPL-800"],
                },
                {
                    "status": "published",
                    "title": "Published screen of a TimTec library",
                    "doi": "10.1000/live",
                    "doi_url": "https://doi.org/10.1000/live",
                    "year": 2018,
                    "author_display": "B. Author; et al.",
                    "journal": "J. Live",
                    "summary": "Listed on the TimTec NPL-800 page.",
                    "snippet": "The methods name the TimTec natural product library.",
                    "collections": ["NPL-800"],
                },
            ]
        }
        live = published_entries(data)
        self.assertEqual(len(live), 1)
        hub = render_hub(live)
        post = render_post(live[0])
        self.assertNotIn("Secret draft", hub)
        self.assertIn("Published screen", hub)
        self.assertIn('"@type": "CollectionPage"', hub)
        self.assertIn('"@type": "ItemList"', hub)
        self.assertIn("ScholarlyArticle", post)
        self.assertIn("https://doi.org/10.1000/live", post)
        self.assertIn("Listed on the TimTec NPL-800 page.", post)
        self.assertIn('href="https://www.timtec.org/news/cited-in-research/', post)
        self.assertNotIn("timtec.net", (hub + post).lower())
        self.assertNotIn("MCL-5000", hub + post)
        self.assertEqual(slug_for(live[0]), "10-1000-live")

    def test_mcl_name_is_not_offered_as_the_product(self):
        html = collection_html(["MCL-5000"], 3)
        self.assertIn("MAC-15000", html)
        self.assertIn("commercial macrocycle screening collection", html)
        self.assertNotIn("MCL-5000", html)
        self.assertNotIn("buy", html.lower())

    def test_pr_body_lists_the_review_fields(self):
        body = build_pr_body(
            [
                {
                    "title": "A TimTec screen",
                    "author_display": "C. Author",
                    "journal": "J. Chem.",
                    "year": 2021,
                    "doi_url": "https://doi.org/10.1000/pr",
                    "snippet": "The library was purchased from TimTec.",
                }
            ],
            1,
        )
        self.assertIn("A TimTec screen", body)
        self.assertIn("C. Author", body)
        self.assertIn("J. Chem.", body)
        self.assertIn("2021", body)
        self.assertIn("https://doi.org/10.1000/pr", body)
        self.assertIn("purchased from TimTec", body)
        self.assertIn("status", body)
        self.assertIn("published", body)


class SitemapTests(unittest.TestCase):
    def test_news_urls_do_not_remove_other_pages(self):
        original = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://www.timtec.org/</loc><lastmod>2026-11-13</lastmod></url>
  <url><loc>https://www.timtec.org/news/</loc><lastmod>2026-11-01</lastmod></url>
  <url><loc>https://www.timtec.org/news/cited-in-research/old/</loc><lastmod>2026-11-01</lastmod></url>
</urlset>
"""
        updated = upsert_sitemap(
            original,
            [("https://www.timtec.org/news/", "2026-11-24")],
            drop_exact="https://www.timtec.org/news/",
        )
        self.assertIn("https://www.timtec.org/</loc>", updated)
        self.assertIn("<lastmod>2026-11-24</lastmod>", updated)
        self.assertIn("cited-in-research/old/", updated)
        replaced = upsert_sitemap(
            updated,
            [("https://www.timtec.org/news/cited-in-research/", "2026-11-24")],
            drop_prefix="https://www.timtec.org/news/cited-in-research",
        )
        self.assertIn("https://www.timtec.org/news/</loc>", replaced)
        self.assertNotIn("cited-in-research/old/", replaced)
        self.assertIn("https://www.timtec.org/news/cited-in-research/</loc>", replaced)
        json.dumps(json.loads('{"ok": true}'))


if __name__ == "__main__":
    unittest.main()
