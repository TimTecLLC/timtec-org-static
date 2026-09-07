# TimTec LLC — GitHub Pages site

Static marketing site for [TimTec LLC](https://www.timtec.org/): screening compounds, building blocks, and pre-designed libraries.

**Working public URL right now:** https://timtecllc.github.io/timtec-org-static/

Custom domain `www.timtec.org` is **not** attached. Do **not** add a root `CNAME` until DNS is stable (an early attach took the site offline). Canonical, Open Graph, and JSON-LD still use `https://www.timtec.org/` as SEO prep.

The IONOS MyWebsite stays **published as rollback** — do not delete or unpublish it. DNS is changed in the IONOS registrar panel, not from this repo. Cutover plan and rollback A/AAAA values: **[docs/MIGRATION-IONOS.md](docs/MIGRATION-IONOS.md)**.

Do **not** change [TimTecLLC/remodelingsupplier-us](https://github.com/TimTecLLC/remodelingsupplier-us).

## URLs

| Host | Role |
| --- | --- |
| https://timtecllc.github.io/timtec-org-static/ | Working GitHub Pages fallback |
| https://www.timtec.org/ | Intended custom domain after DNS is stable |

`SITE_URL` follows the current host at runtime (`github.io`, `www.timtec.org`, or localhost). Static HTML defaults to `https://www.timtec.org`.

Corrected `timtec.net` → `www.timtec.org` 301 map: **[docs/timtec-net-to-org-redirects.md](docs/timtec-net-to-org-redirects.md)**. Apache rules for the **timtec.net host only**: **[docs/htaccess-timtec.net.txt](docs/htaccess-timtec.net.txt)** (not GitHub Pages). Old IONOS slugs on this site use HTML redirect stubs and are omitted from `sitemap.xml`.

Locally:

```bash
python3 -m http.server 8080
```

Then open http://127.0.0.1:8080/

## GitHub Pages

1. **Settings → Pages** → Deploy from a branch → `main`, folder `/` (root).
2. Leave the custom domain **empty** until `www` DNS is a CNAME to `timtecllc.github.io` and apex is not pointed at GitHub early.
3. Do not commit a root `CNAME` file until that cutover is ready.

## Brand and NAP

| Field | Value |
| --- | --- |
| Legal name | TimTec LLC |
| Address | 1950 East Irlo Bronson Memorial Highway Suite 301, Kissimmee, FL 34744 (Orlando area) |
| Phone | 302-292-8500 |
| Fax | 302-292-8520 |
| Email | timtec@timtec.org |
| Orders | orders@timtec.org |
| Billing | ledger@timtec.org |
| Facebook | [TimTecActiMol](https://www.facebook.com/TimTecActiMol) |
| X | [TimTecMolecules](https://x.com/TimTecMolecules) |

Edit the same fields in `js/config.js` if they change. Header has **no** social row; social links are in the footer only.

## External tools (open in a new tab)

| Tool | URL |
| --- | --- |
| Customer Portal | https://timtec-customer-portal.onrender.com |
| TT-BOT | https://timtec-catalog-bot.onrender.com/ |
| Structure Search | https://structure.timtec.org/structure |
| ID / SMILES | https://structure.timtec.org/search |
| SDS | https://structure.timtec.org/msds |
| CoA | https://structure.timtec.org/coa |
| Legacy catalog | http://35.143.96.5:8081/cws/LoginUser.asp |

Homepage: Structure Search as a full-width primary tool button, then ID/SMILES, CoA, TT-BOT, and SDS as secondary buttons (2×2 on small screens, 4-across from 800px; max-width 720px).

## Site map (public)

| Path | Page |
| --- | --- |
| `/` | Home |
| `/r-and-d-chemicals/` | R&D chemicals + catalog-tool links |
| `/screening-collections/` | Library hub |
| `/screening-collections/npl-800/` | NPL-800 |
| `/screening-collections/apexscreen/` | ApexScreen-5040 |
| `/screening-collections/actiglobe-50k/` | ActiGlobe-50K |
| `/screening-collections/actiprobe-10k/` | ActiProbe-10K |
| `/screening-collections/ms-10000/` | MS-10000 diversity library |
| `/screening-collections/ndl-3040/` | NDL-3040 |
| `/screening-collections/fl-500/` | FL-500 |
| `/screening-collections/fbl/` | FBL-3200 fragment-based library |
| `/screening-collections/actitarg-g/` | ActiTarg-G GPCR ligands |
| `/screening-collections/actitarg-k/` | ActiTarg-K kinase modulators |
| `/screening-collections/actitarg-p/` | ActiTarg-P protease inhibitors |
| `/screening-collections/actitarg-s/` | ActiTarg-S serine proteinase inhibitors |
| `/screening-collections/actitarg-i/` | ActiTarg-I potassium-channel modulators |
| `/screening-collections/actitarg-n/` | ActiTarg-N nuclear-receptor ligands |
| `/screening-collections/actitarg-h/` | ActiTarg-H HDAC inhibitors |
| `/screening-collections/actitarg-cns/` | ActiTarg-CNS CNS modulators |
| `/services/` | Synthesis, plating, management, cheminformatics |
| `/contact/` | NAP, EIN/DUNS/UEI/CAGE, mailto form |
| `/about/` | Company history (Kissimmee / Orlando) |
| `/our-customers/` | Selected customer logos in a running strip, plus a crawlable name list |
| `/faq/` | Ordering, freight, formats |
| `/network/` | Published customer / partner figures |
| `/terms/` | Terms of Sale |
| `/privacy/` | How TimTec handles contact and order information |

Public pages include unique title, description, keywords, canonical (`https://www.timtec.org/...`), Open Graph / Twitter tags, and Organization JSON-LD. `robots.txt` and `sitemap.xml` use www.timtec.org URLs.

## Design variants (internal)

The public default is **Lab Teal** (`localStorage` key `timtec-theme-v2`). Comparison themes remain in the repo for review. They are **not** linked from the public header or footer. `/themes/` is `noindex` and disallowed in `robots.txt`.

| Theme | Query | Launcher |
| --- | --- | --- |
| Lab Teal (default) | `?theme=lab-teal` | /themes/lab-teal/ |
| Classic | `?theme=classic` | /themes/classic/ |
| Pharma Navy | `?theme=pharma-navy` | /themes/pharma-navy/ |
| Clean Air | `?theme=clean-air` | /themes/clean-air/ |

Themes are CSS custom properties on `<html data-theme="…">` (`css/themes/*.css`); pages are not duplicated.

## Forms

The contact form is `mailto:timtec@timtec.org`. There is no application server. A hidden `website` field is a honeypot.

## Deploy (GitHub Pages)

`.nojekyll` is present so GitHub does not run Jekyll. Optional workflow: `.github/workflows/pages.yml` (GitHub Actions source). Prefer the simpler **branch / root** setting above.

## About

TimTec LLC — screening compounds and building blocks, Kissimmee / Orlando, Florida.
