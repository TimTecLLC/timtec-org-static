# IONOS → GitHub Pages migration (dual-run)

Bobby confirmed: **flip www.timtec.org DNS to GitHub Pages now.** Apply the records below in the **IONOS registrar / DNS panel**. This repository does not change DNS.

**Do not delete or unpublish the IONOS MyWebsite project.** Leave it published as rollback. Teardown is a later decision.

---

## Status

| Item | State |
| --- | --- |
| IONOS MyWebsite | **Keep published.** Do not delete. |
| This repo | Custom-domain ready (`CNAME` = `www.timtec.org`) |
| Preview | https://timtecllc.github.io/timtec-org-static/ (keep working) |
| Public www.timtec.org | Still IONOS until the registrar DNS change propagates |
| DNS change | Bobby / IONOS panel (not this repo) |

Pattern: [TimTecLLC/remodelingsupplier-us](https://github.com/TimTecLLC/remodelingsupplier-us) already serves a custom domain from GitHub Pages (`CNAME` + Pages custom domain).

---

## Hard rules

1. **Do not delete** the IONOS MyWebsite site, files, or project.
2. **Do not unpublish** IONOS during or right after cutover — it is the rollback.
3. Change DNS only in the IONOS registrar panel (not from this repo, not via GitHub).
4. **Do not touch** the remodelingsupplier-us repo or its DNS.
5. Rollback is **DNS only** — restore the IONOS A/AAAA values below. Do not delete either site.

---

## Observed IONOS DNS (rollback targets)

Recorded before cutover. Confirm in the IONOS DNS panel and take a screenshot before editing.

| Host | Type | Observed value |
| --- | --- | --- |
| `www` | A | `212.227.172.249` |
| `www` | AAAA | `2001:8d8:105:1:0:1:0:1` |
| `@` (apex `timtec.org`) | A | `217.160.0.175` |

IONOS may also have extra A/AAAA, CNAME, or “web forwarding” rows. Copy the **full** current set before changing anything. Rollback = restore those exact rows.

---

## GitHub Pages DNS (cutover targets)

Apply these in the IONOS DNS panel now. Official GitHub Pages addresses ([Managing a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)):

### `www` (recommended primary)

| Type | Host | Value |
| --- | --- | --- |
| CNAME | `www` | `timtecllc.github.io` |

Remove the old IONOS A/AAAA on `www` when you add this CNAME (a name cannot be both CNAME and A).

### Apex `timtec.org` (so bare `timtec.org` also works)

| Type | Host | Value |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| AAAA | `@` | `2606:50c0:8000::153` |
| AAAA | `@` | `2606:50c0:8001::153` |
| AAAA | `@` | `2606:50c0:8002::153` |
| AAAA | `@` | `2606:50c0:8003::153` |

Replace the observed IONOS apex A (`217.160.0.175`) with the four GitHub A records (and add AAAA). If IONOS offers ALIAS/ANAME for the apex, you may use that to `timtecllc.github.io` instead of A/AAAA — not required.

Optional: IONOS URL redirect `timtec.org` → `https://www.timtec.org` if you only want www.

---

## HTTPS / certificate

This repo includes a root `CNAME` file with `www.timtec.org`. GitHub Pages will not finish HTTPS for that name until **public DNS** for `www` points at GitHub (`timtecllc.github.io`).

Until then:

- https://timtecllc.github.io/timtec-org-static/ should keep working.
- https://www.timtec.org/ continues to be IONOS.
- GitHub Settings → Pages may show the custom domain as **DNS check pending** or certificate **not yet issued**. That is normal before cutover.

After DNS propagates, GitHub issues the certificate (often within minutes; can take up to 24 hours). Then enforce HTTPS in Settings → Pages if it is not already on.

---

## Bobby’s DNS checklist (IONOS)

Cutover is approved. Do this in the IONOS DNS / registrar panel. Keep MyWebsite published.

1. **Screenshot / export** the current IONOS DNS zone (www + apex + any redirects).
2. Confirm this repo is on `main` with the `CNAME` file (`www.timtec.org`) and that https://timtecllc.github.io/timtec-org-static/ looks correct.
3. In GitHub → **Settings → Pages**, Custom domain = `www.timtec.org` (the `CNAME` file may already have filled this in). Save.
4. At IONOS DNS:
   - `www` → **CNAME** `timtecllc.github.io` (remove IONOS A/AAAA on `www`).
   - Apex `@` → GitHub **A** / **AAAA** rows above (or IONOS ALIAS).
5. Wait for DNS. Check from an outside network:
   - `dig www.timtec.org CNAME` → `timtecllc.github.io.`
   - `dig www.timtec.org A` → `185.199.108.153`–`111.153` (via the CNAME).
   - `curl -I https://www.timtec.org/` → GitHub Pages (not `server: IONOS Webserver` / `212.227.172.249`).
6. Confirm GitHub Pages certificate is issued and HTTPS works.
7. Walk Home, Contact, Screening, Services, Our Customers. Confirm theme (Lab Teal default) and relative nav.
8. **Leave IONOS MyWebsite published** for days or weeks as fallback.
9. Teardown IONOS **only** after Bobby explicitly confirms. That is a later decision, not part of cutover.

---

## Rollback (if GitHub Pages misbehaves after DNS)

1. At IONOS, restore the previous records:
   - `www` A `212.227.172.249`
   - `www` AAAA `2001:8d8:105:1:0:1:0:1`
   - apex A `217.160.0.175`
   - plus any other rows you captured in the pre-change screenshot.
2. Do **not** delete this GitHub repo or the IONOS project.
3. Traffic returns to IONOS MyWebsite once DNS propagates.

---

## What this repo already did (prep)

- Root `CNAME` = `www.timtec.org` (same idea as remodelingsupplier.us).
- `SITE_URL` / canonical / `og:url` / `og:image` / JSON-LD resolve from the **current host**:
  - `www.timtec.org` or `timtec.org` → `https://www.timtec.org`
  - `timtecllc.github.io` → `https://timtecllc.github.io/timtec-org-static`
  - `localhost` → local origin (preview still works)
- Footer copy says migration is in progress; IONOS is retained as fallback.
- `sitemap.xml` / `robots.txt` use `https://www.timtec.org` so they are correct **after** cutover. Until then, www still serves IONOS’s own files.

---

## After cutover (later, not now)

- Keep IONOS MyWebsite published until Bobby is satisfied.
- Then, and only then, consider unpublishing or deleting IONOS.
- Search Console: add/verify www if needed; submit `https://www.timtec.org/sitemap.xml`.
