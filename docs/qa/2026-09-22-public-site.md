# Public site QA — 22 September 2026

Live check: `https://www.timtec.org/` is this repository on GitHub Pages (`server: GitHub.com`, HTTP 200). `https://timtecllc.github.io/timtec-org-static/` redirects to www while the Pages custom domain is attached.

Related hosts checked the same day (HTTP 200): `structure.timtec.org` structure search, ID/SMILES, CoA, SDS, and `/api/site-status`; TT-BOT at `timtec-catalog-bot.onrender.com`; Customer Portal at `timtec-customer-portal.onrender.com`. TT-BOT is an outbound link, not an inline chat embed. There is no Grok Bot embed in this site.

## Fixed

| Issue | Where | What changed |
| --- | --- | --- |
| Home hero image cropped as a square cover, with no text alternative | Home | Molecule image is now a real `<img>` with alt text, shown at a fixed square instead of a full-bleed crop. Background keeps the light teal wash. |
| Catalog tool row missing on FAQ, Terms, and TimTec Network | FAQ, Terms, Network | Same Structure Search / ID-SMILES / CoA / TT-BOT / SDS row as the home page. Also added on Contact, R&D Chemicals, and the screening-collections hub. |
| R&D tool row omitted CoA, SDS, and TT-BOT | R&D Chemicals | Full catalog row. Legacy catalog login remains a text link. |
| Inventory wording did not name A01/A02/A03, and lead times disagreed | Home, R&D Chemicals, FAQ, screening hub | A01 and A02 are Orlando in-stock (overnight–2 days; 180,000 ActiMol U.S. compounds). A03 is extended overseas stock (3–4 weeks, confirm on the quote; 1.5 million compounds on the R&D page). The old FAQ row that split “extended” (1–2 weeks) from “overseas” (3–4 weeks) is one A03 row. |
| Contact block omitted the website | Every public footer, Contact card, Services quote | Visible block is TimTec, LLC; 1950 East Irlo Bronson Memorial Highway, Suite 301, Kissimmee, FL 34744; phone 302-292-8500; fax 302-292-8520; timtec@timtec.org; www.timtec.org. |
| Footer Site column skipped Network | Public footers | Network sits with FAQ. |
| Compound-box images declared the wrong height | R&D Chemicals | Width/height set to the file size, 1600×1343. |
| 2026 catalog button used an absolute www URL | Home | Relative `assets/…pdf` so local and preview hosts open the file in this repo. |
| Mobile menu could grow past the screen | Header | Open menu scrolls inside the viewport. Mid-width nav padding is slightly tighter so the desktop items fit. |
| README and migration notes still said www was not on GitHub Pages | README, `docs/MIGRATION-IONOS.md`, `js/config.js` | www is documented as live. Apex failure is called out as registrar DNS. |

## Checked, no change required

- No Tampa Bay Plaza address, no `timtec.net` contact address, and no MCL-5000 purchasable listing in the HTML.
- The 1995 history line that says www.TimTec.net launched is a dated company-history fact, not a contact address.
- Local image references in HTML all resolve. Customer marks, including the small Mount Sinai and Fate files, are real logo files, not broken links.
- Library and services photos already have descriptive alt text. Logo alt is “TimTec LLC”.
- Kissimmee NAP was already in JSON-LD, the contact card, and footers before this pass. This pass adds the website and the “TimTec, LLC” contact heading.
- Old IONOS slugs under `/contact-us/…` are HTML redirects to the current pages.

## Still open

| Issue | Why it is still open |
| --- | --- |
| `https://timtec.org/` TLS internal error | Apex A `217.160.0.175` and AAAA `2001:8d8:100f:f000::200` are still the old IONOS host. HTTP is nginx 404. GitHub Pages `CNAME` only covers `www.timtec.org`. Fix in the IONOS DNS panel: GitHub Pages apex A/AAAA records in `docs/MIGRATION-IONOS.md`, or an HTTPS redirect to `https://www.timtec.org/`. Do not delete the IONOS site until that cutover is confirmed. |
| `timtec.net` → www 301s | Still a host-level Apache change (`docs/htaccess-timtec.net.txt`). GitHub Pages cannot emit those redirects. |
| Some customer logos are very small source files | They load. Replacing them needs official artwork; this pass does not redraw third-party marks. |
| Legacy catalog is plain HTTP (`35.143.96.5:8081`) | Left as the existing bookmark. It is no longer a primary button. |
| Theme comparison pages under `/themes/` | Internal, `noindex`. Not part of the public nav. |

## Not claimed

No new library sizes, purity figures, or purchasable collections were added. MCL-5000 is not listed. Stock counts (180,000 and 1.5 million) and the overnight–2 day / 3–4 week timings were already published on the site; they are now tied to A01/A02 and A03 instead of three overlapping labels.
