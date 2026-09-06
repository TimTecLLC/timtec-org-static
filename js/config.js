/**
 * TimTec LLC — public site configuration
 * Intended production host is www.timtec.org. Custom domain stays off until
 * DNS is stable. IONOS MyWebsite remains published as rollback — do not delete
 * (see docs/MIGRATION-IONOS.md).
 */
window.SITE_CONFIG = {
  BUSINESS_NAME: "TimTec LLC",
  PHONE: "302-292-8500",
  FAX: "302-292-8520",
  EMAIL: "timtec@timtec.org",
  ORDERS_EMAIL: "orders@timtec.org",
  BILLING_EMAIL: "ledger@timtec.org",
  ADDRESS: "1950 East Irlo Bronson Memorial Highway Suite 301, Kissimmee, FL 34744",
  ADDRESS_LOCALITY: "Kissimmee",
  ADDRESS_REGION: "FL",
  ADDRESS_POSTAL: "34744",
  FACEBOOK_URL: "https://www.facebook.com/TimTecActiMol",
  TWITTER_URL: "https://x.com/TimTecMolecules",
  TT_BOT_URL: "https://timtec-catalog-bot.onrender.com/",
  CUSTOMER_PORTAL_URL: "https://timtec-customer-portal.onrender.com",
  STRUCTURE_URL: "http://74.208.206.139/structure",
  ID_SMILES_URL: "http://74.208.206.139/search",
  SDS_URL: "http://74.208.206.139/msds",
  COA_URL: "http://74.208.206.139/coa",
  LEGACY_URL: "http://35.143.96.5:8081/cws/LoginUser.asp",
  CATALOG_URL:
    "https://www.timtec.org/wp-content/uploads/go-x/u/48e2d4a7-88cf-47b8-9be6-7dab9704a98c/TimTec_Tim-Tec-Product-and-Services-catalog-2026.pdf",
  EIN: "92-1623387",
  DUNS: "124563630",
  UEI: "RHR9P95ATEU3",
  CAGE: "9PRN8",
  PRODUCTION_URL: "https://www.timtec.org",
  PREVIEW_URL: "https://timtecllc.github.io/timtec-org-static",
  SITE_URL: "https://www.timtec.org",
};

(function resolveSiteUrl() {
  var cfg = window.SITE_CONFIG;
  var host = "";
  try {
    host = String((window.location && window.location.hostname) || "").toLowerCase();
  } catch (err) {
    return;
  }
  if (host === "www.timtec.org" || host === "timtec.org") {
    cfg.SITE_URL = cfg.PRODUCTION_URL;
    return;
  }
  if (host === "timtecllc.github.io") {
    cfg.SITE_URL = cfg.PREVIEW_URL;
    return;
  }
  if (host === "localhost" || host === "127.0.0.1") {
    cfg.SITE_URL = String((window.location && window.location.origin) || "").replace(/\/$/, "");
  }
})();
