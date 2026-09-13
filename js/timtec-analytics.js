/**
 * First-party pageview beacon for TimTec Analytics.
 * POSTs path and referrer only — no names, emails, or other PII.
 * Failures are ignored so a blocked or down collector never affects the page.
 */
(function () {
  "use strict";

  var COLLECT_URL = "https://structure.timtec.org/api/analytics/collect";
  var SITE = "https://www.timtec.org";
  var SESSION_KEY = "timtec-analytics-session";

  if (window.__TIMTEC_ANALYTICS_SENT) return;
  window.__TIMTEC_ANALYTICS_SENT = true;

  function newSessionId() {
    try {
      if (window.crypto && typeof window.crypto.randomUUID === "function") {
        return window.crypto.randomUUID();
      }
    } catch (err) {
      /* fall through */
    }
    return "tt-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 12);
  }

  function sessionId() {
    try {
      var stored = window.sessionStorage.getItem(SESSION_KEY);
      if (stored) return stored;
      var created = newSessionId();
      window.sessionStorage.setItem(SESSION_KEY, created);
      return created;
    } catch (err) {
      return newSessionId();
    }
  }

  function pagePath() {
    try {
      return window.location.pathname || "/";
    } catch (err) {
      return "/";
    }
  }

  function referrer() {
    try {
      return document.referrer || "";
    } catch (err) {
      return "";
    }
  }

  function send(payload) {
    var body = JSON.stringify(payload);
    try {
      if (typeof fetch === "function") {
        fetch(COLLECT_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: body,
          keepalive: true,
          credentials: "omit",
        }).catch(function () {
          /* fail silently */
        });
        return;
      }
    } catch (err) {
      /* fail silently */
    }
    try {
      if (navigator.sendBeacon) {
        navigator.sendBeacon(COLLECT_URL, new Blob([body], { type: "application/json" }));
      }
    } catch (err) {
      /* fail silently */
    }
  }

  try {
    send({
      type: "pageview",
      site: SITE,
      path: pagePath(),
      referrer: referrer(),
      sessionId: sessionId(),
    });
  } catch (err) {
    /* fail silently */
  }
})();
