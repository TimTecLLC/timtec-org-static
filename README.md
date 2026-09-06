# TimTec LLC — GitHub Pages site

Static rebuild of [www.timtec.org](https://www.timtec.org/). Patterned after [TimTecLLC/remodelingsupplier-us](https://github.com/TimTecLLC/remodelingsupplier-us) (static HTML/CSS/JS, no WordPress).

**Migration from IONOS is in progress.** GitHub Pages is the intended host for `www.timtec.org`. The IONOS MyWebsite stays **published as rollback** — do not delete or unpublish it. DNS is changed in the IONOS registrar panel, not from this repo.

Cutover plan, GitHub Pages records, and rollback A/AAAA values: **[docs/MIGRATION-IONOS.md](docs/MIGRATION-IONOS.md)**.

## URLs

| Host | Role |
| --- | --- |
| https://www.timtec.org/ | Custom domain (serves this site **after** IONOS DNS points at GitHub) |
| https://timtecllc.github.io/timtec-org-static/ | Preview / fallback URL (keep working) |

`CNAME` in the repo root is exactly `www.timtec.org`. GitHub cannot finish HTTPS for that name until public DNS for `www` is a CNAME to `timtecllc.github.io`.

`SITE_URL`, canonical, `og:url`, `og:image`, and JSON-LD follow the current host (`www.timtec.org`, `timtecllc.github.io`, or localhost). Static HTML defaults to `https://www.timtec.org`.

Locally:

```bash
python3 -m http.server 8080
```

Then open http://127.0.0.1:8080/

## GitHub Pages

1. **Settings → Pages** → Deploy from a branch → `main`, folder `/` (root).
2. Custom domain: `www.timtec.org` (matches the `CNAME` file).
3. Enforce HTTPS after the certificate issues (needs the IONOS DNS change first).

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

Cube logo is copied from the IONOS site (`assets/logo.jpg`).

## External tools (open in a new tab)

| Tool | URL |
| --- | --- |
| TT-BOT | https://timtec-catalog-bot.onrender.com/ |
| Structure Search | http://74.208.206.139/structure |
| ID / SMILES | http://74.208.206.139/search |
| SDS | http://74.208.206.139/msds |
| CoA | http://74.208.206.139/coa |
| Legacy catalog | http://35.143.96.5:8081/cws/LoginUser.asp |

Homepage: centered 2×2 colored buttons (Structure Search, ID/SMILES, CoA, TT-BOT) plus a full-width SDS button (max-width 720px).

## Site map

| Path | Page |
| --- | --- |
| `/` | Home |
| `/r-and-d-chemicals/` | R&D chemicals + catalog-tool links |
| `/screening-collections/` | Library hub |
| `/screening-collections/npl-800/` | NPL-800 |
| `/screening-collections/apexscreen/` | ApexScreen-5040 |
| `/screening-collections/actiglobe-50k/` | ActiGlobe-50K |
| `/screening-collections/actiprobe-10k/` | ActiProbe-10K |
| `/screening-collections/ndl-3040/` | NDL-3040 |
| `/screening-collections/fl-500/` | FL-500 |
| `/services/` | Synthesis, plating, management, cheminformatics |
| `/contact/` | NAP, EIN/DUNS/UEI/CAGE, mailto form |
| `/about/` | Company history (Kissimmee / Orlando, not Tampa) |
| `/our-customers/` | Selected customer logos in a running strip, plus a crawlable name list |
| `/faq/` | Ordering, freight, formats |
| `/network/` | Published customer / partner figures |
| `/terms/` | Terms of Sale |
| `/privacy/` | Notes for this static host |
| `/themes/` | Design gallery (Classic, Lab Teal, Pharma Navy, Clean Air) |

Copy was adapted from www.timtec.org and useful catalog text on www.timtec.net. Stale Tampa ship-from lines were rewritten to Kissimmee / Orlando. Literature citations are those TimTec already published; no new efficacy claims were added.

`/our-customers/` is a running logo strip (not a grid). Historical logos come from [timtec.net/our-customers.html](https://www.timtec.net/our-customers.html) (`assets/customers/`). The dsm-firmenich wordmark is included as a logo tile. Names without a logo file (University of Sydney, Al Ain University, New York Blood Center / NYBC, Duke, UT Southwestern, Ginkgo Bioworks, and others) are text tiles in the strip and in a crawlable name list on the page. Non-operating brands were removed. MolPort and Mcule are not listed as primary customers. No endorsement language. The public page does not show build notes or file-path instructions.

## Design variants

The default look is **Lab Teal**. Choosing a theme writes `localStorage` key `timtec-theme-v2` so Contact, Our Customers, Screening, and the rest of the site stay in that finish until another is picked.

| Theme | Query | Launcher |
| --- | --- | --- |
| Classic | `?theme=classic` | /themes/classic/ |
| Lab Teal (default) | `?theme=lab-teal` | /themes/lab-teal/ |
| Pharma Navy | `?theme=pharma-navy` | /themes/pharma-navy/ |
| Clean Air | `?theme=clean-air` | /themes/clean-air/ |

Gallery: `/themes/`. A “Design previews” chip in the header and a “Theme gallery” footer link stay on this static host. Themes are CSS custom properties on `<html data-theme="…">` (`css/themes/*.css`); pages are not duplicated.

## Forms

The contact form is `mailto:timtec@timtec.org` (same idea as the remodeling-supplier site). There is no application server. A hidden `website` field is a honeypot.

## Deploy (GitHub Pages)

`.nojekyll` is present so GitHub does not run Jekyll. Optional workflow: `.github/workflows/pages.yml` (GitHub Actions source). Prefer the simpler **branch / root** setting above.

## About

TimTec LLC — screening compounds and building blocks, Kissimmee / Orlando, Florida.
