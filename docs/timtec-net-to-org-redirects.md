# timtec.net → www.timtec.org redirects (corrected)

Bobby’s original `.net` → `.org` 301 table sent many URLs to **old IONOS paths** (`/contact-us/…`, hyphenated library slugs, and similar). Those paths **404 on the live GitHub Pages site**. This document is the **corrected** map.

Destinations below match pages that exist on [www.timtec.org](https://www.timtec.org/) (or an intentional external host). Relative destinations are on `https://www.timtec.org`.

## Where this config runs

**Apache / Nginx rewrite rules must be installed on the `timtec.net` host — not on GitHub Pages.**

GitHub Pages cannot apply `.htaccess` or Nginx server blocks. The ready Apache file in this repo is [`htaccess-timtec.net.txt`](htaccess-timtec.net.txt). Copy it to the **timtec.net** web root as `.htaccess` (or merge the rules into the existing vhost). Do not commit a root `.htaccess` here for Pages.

GitHub Pages also cannot emit a true HTTP 301 for old **www.timtec.org** IONOS slugs. Those are handled separately with HTML stubs (see [Old IONOS path stubs](#old-ionos-path-stubs-on-wwwtimtecorg)).

---

## Corrected 301 map (timtec.net)

| Source on `timtec.net` | Destination |
| --- | --- |
| `/` (and `index.html`) | `https://www.timtec.org/` |
| `about-us.html` | `https://www.timtec.org/about/` |
| `timtec-network.html` | `https://www.timtec.org/network/` |
| `our-partners.html` | `https://www.timtec.org/network/` |
| `our-customers.html` | `https://www.timtec.org/our-customers/` |
| `contact-us.html` | `https://www.timtec.org/contact/` |
| `faqs.html` | `https://www.timtec.org/faq/` |
| `faqs/*` | `https://www.timtec.org/faq/` |
| `terms-of-sale.html` | `https://www.timtec.org/terms/` |
| `screening-compounds` | `https://www.timtec.org/r-and-d-chemicals/` |
| `building-blocks` | `https://www.timtec.org/r-and-d-chemicals/` |
| `download-databases` | `https://www.timtec.org/r-and-d-chemicals/` |
| `structure-search.html` | `http://74.208.206.139/structure` |
| `screening-compound-libraries` | `https://www.timtec.org/screening-collections/` |
| `libraries/*` | `https://www.timtec.org/screening-collections/` |
| `myriascreen` | `https://www.timtec.org/screening-collections/myriascreen/` |
| `myriascreen-diversity-collection` | `https://www.timtec.org/screening-collections/myriascreen/` |
| `plant-extracts` | `https://www.timtec.org/screening-collections/` |
| `actitarg-*` | `https://www.timtec.org/screening-collections/` |
| `acticom` | `https://www.timtec.org/screening-collections/` |
| `privileged-structures` | `https://www.timtec.org/screening-collections/` |
| `fbl-fragment` | `https://www.timtec.org/screening-collections/fbl/` |
| `fbl-fragment-based-library` | `https://www.timtec.org/screening-collections/fbl/` |
| `actiglobe-50k.html` | `https://www.timtec.org/screening-collections/actiglobe-50k/` |
| `actiprobe-series` | `https://www.timtec.org/screening-collections/actiprobe-10k/` |
| `actiprobe-10k` (and `*10k*` ActiProbe paths) | `https://www.timtec.org/screening-collections/actiprobe-10k/` |
| `apexscreen` | `https://www.timtec.org/screening-collections/apexscreen/` |
| `npl-pure-natural-compounds` | `https://www.timtec.org/screening-collections/npl-800/` |
| `natural-products-library` | `https://www.timtec.org/screening-collections/npl-800/` |
| `ndl-derivatives` | `https://www.timtec.org/screening-collections/ndl-3040/` |
| `flavonoids` | `https://www.timtec.org/screening-collections/fl-500/` |
| `services` | `https://www.timtec.org/services/` |
| `compound-management` | `https://www.timtec.org/services/` |
| `custom-synthesis` | `https://www.timtec.org/services/` |
| `cheminformatics` | `https://www.timtec.org/services/` |
| `news-and-articles` | `https://www.timtec.org/about/` |
| `timtec-in-publications` | `https://www.timtec.org/about/` |
| `software` | `http://www.chemdbsoft.com/` |
| `chemdbsoft` | `http://www.chemdbsoft.com/` |
| `sitemap.html` | `https://www.timtec.org/` |
| Catch-all (any other `timtec.net` path) | `https://www.timtec.org/` |

Notes:

- There is **no publications page yet**. News and “TimTec in publications” URLs go to `/about/`.
- The Apache file also accepts an optional `.html` suffix and trailing slash on the sources that were listed without an extension (legacy CMS URLs vary).
- External destinations (`structure-search.html` → the structure-search host, `software` / `chemdbsoft` → ChemDBsoft) stay on those hosts. They are not rewritten to IONOS or GitHub paths.

---

## Old IONOS path stubs on www.timtec.org

Bookmarks and search results still hit IONOS slugs on **www.timtec.org**. Those slugs 404 on GitHub Pages. This repo adds lightweight HTML stubs so those URLs still land on a current page.

Each stub is `noindex`, omitted from `sitemap.xml`, and redirects with:

1. `<link rel="canonical">` to the destination
2. `<meta http-equiv="refresh">`
3. `location.replace(...)`

| Stub on `www.timtec.org` | Destination |
| --- | --- |
| `/contact-us/` | `/contact/` |
| `/contact-us/about-timtec/` | `/about/` |
| `/contact-us/timtec-network/` | `/network/` |
| `/contact-us/faq/` | `/faq/` |
| `/contact-us/terms-of-sale/` | `/terms/` |
| `/contact-us/tt-in-publications/` | `/about/` |
| `/screening-collections/acti-globe-50-k/` | `/screening-collections/actiglobe-50k/` |
| `/screening-collections/natural-compound-library-npl-800/` | `/screening-collections/npl-800/` |
| `/structure-search/` | `http://74.208.206.139/structure` |

These are **not** HTTP 301 responses. They are a GitHub Pages workaround until `timtec.net` hosting can issue real 301s and until search indexes drop the old IONOS slugs.
