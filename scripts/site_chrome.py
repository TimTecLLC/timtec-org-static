"""Shared header, footer, and sitemap helpers for generated news pages."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITEMAP_PATH = ROOT / "sitemap.xml"
SITE = "https://www.timtec.org"

ORG_ID = f"{SITE}/#organization"
SITE_ID = f"{SITE}/#website"


def prefix(depth: int) -> str:
    return "../" * depth


def json_ld(data: object) -> str:
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    return raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def organization() -> dict:
    return {
        "@type": "Organization",
        "@id": ORG_ID,
        "name": "TimTec LLC",
        "url": f"{SITE}/",
        "logo": f"{SITE}/assets/logo.jpg",
        "email": "timtec@timtec.org",
        "telephone": "+1-302-292-8500",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "1950 East Irlo Bronson Memorial Highway Suite 301",
            "addressLocality": "Kissimmee",
            "addressRegion": "FL",
            "postalCode": "34744",
            "addressCountry": "US",
        },
        "sameAs": [
            "https://www.facebook.com/TimTecActiMol",
            "https://x.com/TimTecMolecules",
        ],
    }


def news_nav(pre: str, current: str | None) -> str:
    industry = ' class="is-current"' if current == "industry" else ""
    cited = ' class="is-current"' if current == "cited" else ""
    return f"""          <li class="nav-item has-dropdown" data-dropdown>
            <button class="has-sub" type="button" aria-expanded="false" aria-haspopup="true">News</button>
            <ul class="submenu">
              <li><a href="{pre}news/"{industry}>Industry News</a></li>
              <li><a href="{pre}news/cited-in-research/"{cited}>Cited in Research</a></li>
            </ul>
          </li>"""


def header(depth: int, current: str | None) -> str:
    pre = prefix(depth)
    return f"""    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header">
      <div class="wrap header-inner">
        <a class="logo" href="{pre}index.html">
          <img src="{pre}assets/logo.jpg" alt="TimTec LLC" width="188" height="94" />
        </a>
        <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">
          <span></span>
        </button>
      <nav id="site-nav" class="site-nav" data-site-nav aria-label="Primary">
        <ul class="nav-list">
          <li class="nav-item has-dropdown" data-dropdown>
            <button class="has-sub" type="button" aria-expanded="false" aria-haspopup="true">R&amp;D Chemicals</button>
            <ul class="submenu">
              <li><a href="{pre}r-and-d-chemicals/">R&amp;D Chemicals overview</a></li>
              <li><a href="https://structure.timtec.org/structure" target="_blank" rel="noopener noreferrer">Structure Search <span class="ext-mark" aria-hidden="true">↗</span></a></li>
              <li><a href="https://structure.timtec.org/search" target="_blank" rel="noopener noreferrer">ID / SMILES <span class="ext-mark" aria-hidden="true">↗</span></a></li>
              <li><a href="https://structure.timtec.org/msds" target="_blank" rel="noopener noreferrer">SDS <span class="ext-mark" aria-hidden="true">↗</span></a></li>
              <li><a href="https://structure.timtec.org/coa" target="_blank" rel="noopener noreferrer">CoA <span class="ext-mark" aria-hidden="true">↗</span></a></li>
            </ul>
          </li>
          <li class="nav-item has-dropdown" data-dropdown>
            <button class="has-sub" type="button" aria-expanded="false" aria-haspopup="true">Screening Collections</button>
            <ul class="submenu">
              <li><a href="{pre}screening-collections/">All libraries</a></li>
              <li><a href="{pre}screening-collections/npl-800/">NPL-800</a></li>
              <li><a href="{pre}screening-collections/apexscreen/">ApexScreen</a></li>
              <li><a href="{pre}screening-collections/actiglobe-50k/">ActiGlobe-50K</a></li>
              <li><a href="{pre}screening-collections/actiprobe-10k/">ActiProbe-10K</a></li>
              <li><a href="{pre}screening-collections/ms-10000/">MS-10000</a></li>
              <li><a href="{pre}screening-collections/ndl-3040/">NDL-3040</a></li>
              <li><a href="{pre}screening-collections/fl-500/">FL-500</a></li>
              <li><a href="{pre}screening-collections/fbl/">FBL</a></li>
              <li><a href="{pre}screening-collections/mac-15000/">MAC-15000</a></li>
              <li><a href="{pre}screening-collections/actitarg-g/">ActiTarg-G</a></li>
              <li><a href="{pre}screening-collections/actitarg-k/">ActiTarg-K</a></li>
              <li><a href="{pre}screening-collections/actitarg-p/">ActiTarg-P</a></li>
              <li><a href="{pre}screening-collections/actitarg-s/">ActiTarg-S</a></li>
              <li><a href="{pre}screening-collections/actitarg-i/">ActiTarg-I</a></li>
              <li><a href="{pre}screening-collections/actitarg-n/">ActiTarg-N</a></li>
              <li><a href="{pre}screening-collections/actitarg-h/">ActiTarg-H</a></li>
              <li><a href="{pre}screening-collections/actitarg-cns/">ActiTarg-CNS</a></li>
            </ul>
          </li>
          <li><a href="{pre}services/">Services</a></li>
{news_nav(pre, current)}
          <li class="nav-item has-dropdown" data-dropdown>
            <button class="has-sub" type="button" aria-expanded="false" aria-haspopup="true">Contact</button>
            <ul class="submenu">
              <li><a href="{pre}contact/">Contact</a></li>
              <li><a href="{pre}about/">About</a></li>
              <li><a href="{pre}our-customers/">Our Customers</a></li>
              <li><a href="{pre}faq/">FAQ</a></li>
              <li><a href="{pre}network/">Network</a></li>
              <li><a href="{pre}terms/">Terms of Sale</a></li>
              <li><a href="{pre}privacy/">Privacy</a></li>
            </ul>
          </li>
          <li><a href="https://timtec-customer-portal.onrender.com">Customer Portal</a></li>
          <li><a href="https://timtec-catalog-bot.onrender.com/" target="_blank" rel="noopener noreferrer">TT-BOT <span class="ext-mark" aria-hidden="true">↗</span></a></li>
        </ul>
      </nav>
      </div>
    </header>"""


def footer(depth: int) -> str:
    pre = prefix(depth)
    return f"""    <footer class="site-footer">
      <div class="wrap footer-grid">
        <div>
          <h2>TimTec, LLC</h2>
          <p>Screening compounds, building blocks, and library formatting for drug-discovery groups. Orlando-area office in Kissimmee, Florida. Founded 1995.</p>
          <p>
            1950 East Irlo Bronson Memorial Highway<br />
            Suite 301<br />
            Kissimmee, FL 34744
          </p>
          <p>
            <a href="tel:+13022928500">302-292-8500</a><br />
            <span class="phone-note">Our long-standing line, answered at our Kissimmee, FL facility.</span><br />
            Fax 302-292-8520<br />
            <a href="mailto:timtec@timtec.org">timtec@timtec.org</a><br />
            <a href="{SITE}/">www.timtec.org</a>
          </p>
        </div>
        <div>
          <h2>Catalog tools</h2>
          <ul>
            <li><a href="http://35.143.96.5:8081/cws/LoginUser.asp" target="_blank" rel="noopener noreferrer">Legacy catalog login</a></li>
          </ul>
        </div>
        <div>
          <h2>Site</h2>
          <ul>
            <li><a href="{pre}r-and-d-chemicals/">R&amp;D Chemicals</a></li>
            <li><a href="{pre}screening-collections/">Screening Collections</a></li>
            <li><a href="{pre}services/">Services</a></li>
            <li><a href="{pre}news/">News</a></li>
            <li><a href="{pre}contact/">Contact</a></li>
            <li><a href="{pre}about/">About</a></li>
            <li><a href="{pre}our-customers/">Our Customers</a></li>
            <li><a href="{pre}faq/">FAQ</a></li>
            <li><a href="{pre}network/">Network</a></li>
          </ul>
        </div>
        <div>
          <h2>Follow</h2>
          <p class="socials">
            <a href="https://www.facebook.com/TimTecActiMol" target="_blank" rel="noopener noreferrer">Facebook · TimTecActiMol</a>
            <a href="https://x.com/TimTecMolecules" target="_blank" rel="noopener noreferrer">X · TimTecMolecules</a>
          </p>
          <p><a href="{pre}terms/">Terms of Sale</a> · <a href="{pre}privacy/">Privacy</a></p>
        </div>
      </div>
      <div class="wrap legal">
        <p>© 1995–<span data-year>2026</span> TimTec LLC. All rights reserved. Products are for research and development use only and are not for human or animal consumption.</p>
      </div>
    </footer>
    <script src="{pre}js/config.js"></script>
    <script src="{pre}js/site.js"></script>
    <script src="{pre}js/timtec-analytics.js"></script>"""


def render_document(
    *,
    depth: int,
    title: str,
    description: str,
    keywords: str,
    canonical_path: str,
    graph: list,
    main_html: str,
    current: str | None,
    robots: str = "index,follow",
) -> str:
    pre = prefix(depth)
    canonical = f"{SITE}{canonical_path}"
    ld = {
        "@context": "https://schema.org",
        "@graph": [organization(), *graph],
    }
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <script src="{pre}js/theme-boot.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <meta name="description" content="{description}" />
    <meta name="keywords" content="{keywords}" />
    <meta name="robots" content="{robots}" />
    <meta name="author" content="TimTec LLC" />
    <meta name="geo.region" content="US-FL" />
    <meta name="geo.placename" content="Kissimmee, Orlando" />
    <meta name="msvalidate.01" content="4D59D17FB117B72AB09A91B9EE615407" />
    <link rel="canonical" href="{canonical}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="TimTec LLC" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:image" content="{SITE}/assets/logo.jpg" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{SITE}/assets/logo.jpg" />
    <link rel="icon" href="{pre}assets/favicon.png" type="image/png" />
    <link rel="apple-touch-icon" href="{pre}assets/favicon.png" />
    <meta name="theme-color" content="#0d4f4b" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&amp;family=Source+Serif+4:opsz,wght@8..60,500;8..60,650&amp;display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="{pre}css/styles.css" />
    <link rel="stylesheet" href="{pre}css/themes.css" />
    <script type="application/ld+json">
{json_ld(ld)}
    </script>
  </head>
  <body>
{header(depth, current)}
    <main id="main">
{main_html}
    </main>
{footer(depth)}
  </body>
</html>
"""


def upsert_sitemap(text: str, entries: list[tuple[str, str]], *, drop_prefix: str = "", drop_exact: str = "") -> str:
    """Replace selected sitemap URLs and append the new ones before </urlset>."""
    kept: list[str] = []
    newline = "\n" if text.endswith("\n") else ""
    for line in text.splitlines():
        match = re.search(r"<loc>([^<]+)</loc>", line)
        if match:
            loc = match.group(1).strip()
            if drop_exact and loc == drop_exact:
                continue
            if drop_prefix and loc.startswith(drop_prefix):
                continue
        kept.append(line)
    body = "\n".join(kept)
    if "</urlset>" not in body:
        raise ValueError("sitemap.xml is missing </urlset>")
    block = "\n".join(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod></url>" for loc, lastmod in entries)
    if block:
        body = body.replace("</urlset>", block + "\n</urlset>", 1)
    if newline and not body.endswith("\n"):
        body += "\n"
    return body


def write_sitemap(entries: list[tuple[str, str]], *, drop_prefix: str = "", drop_exact: str = "") -> None:
    current = SITEMAP_PATH.read_text(encoding="utf-8")
    updated = upsert_sitemap(current, entries, drop_prefix=drop_prefix, drop_exact=drop_exact)
    if updated != current:
        SITEMAP_PATH.write_text(updated, encoding="utf-8")
