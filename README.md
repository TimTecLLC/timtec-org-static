# TimTec LLC — static test site

Parallel **GitHub Pages** rebuild of [www.timtec.org](https://www.timtec.org/). Patterned after [TimTecLLC/remodelingsupplier-us](https://github.com/TimTecLLC/remodelingsupplier-us) (static HTML/CSS/JS, no WordPress, no IONOS MyWebsite).

**Live IONOS / www.timtec.org is not modified by this repository.**

## Preview URL

**https://timtecllc.github.io/timtec-org-static/**

This repo’s GitHub token cannot flip the Pages switch (no admin). Bobby (or anyone with Settings access) needs one click after this branch is on `main` (or point Pages at this branch first):

1. GitHub → **Settings → Pages**
2. Build and deployment: **Deploy from a branch**
3. Branch **`main`**, folder **`/`** (root)
4. Save. The `github.io` URL above appears in a minute or two.

Do **not** add a `CNAME` for www.timtec.org — this is the parallel test site only.

Locally:

```bash
python3 -m http.server 8080
```

Then open http://127.0.0.1:8080/

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

Cube logo is copied from the live IONOS site (`assets/logo.jpg`).

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
| `/our-customers/` | Selected customer logos from timtec.net plus later name tiles |
| `/faq/` | Ordering, freight, formats |
| `/network/` | Published customer / partner figures |
| `/terms/` | Terms of Sale |
| `/privacy/` | Notes for this static host |

Copy was adapted from www.timtec.org and useful catalog text on www.timtec.net. Stale Tampa ship-from lines were rewritten to Kissimmee / Orlando. Literature citations are those TimTec already published; no new efficacy claims were added.

`/our-customers/` logos come from [timtec.net/our-customers.html](https://www.timtec.net/our-customers.html) (`assets/customers/`). Names without a logo file (2023–2026 shipping end-customers such as Firmenich, University of Sydney, Al Ain University, New York Blood Center / NYBC, Duke, UT Southwestern, Ginkgo Bioworks, and others) are text tiles in `js/customers-extra.js`. MolPort and Mcule are not listed as primary customers. No endorsement language.

## Forms

The contact form is `mailto:timtec@timtec.org` (same idea as the remodeling-supplier site). There is no application server. A hidden `website` field is a honeypot.

## Deploy (GitHub Pages)

`.nojekyll` is present so GitHub does not run Jekyll. Optional workflow: `.github/workflows/pages.yml` (GitHub Actions source). Prefer the simpler **branch / root** setting above.

## About

TimTec LLC — screening compounds and building blocks, Kissimmee / Orlando, Florida.
