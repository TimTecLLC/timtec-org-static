/**
 * Public service-status LED strip. Mirrors structure.timtec.org
 * (TimTecLLC/timtec-list-search SiteStatusBar) and reads the live
 * probe API — never marks a service online without a 2xx/3xx payload.
 */
(function () {
  "use strict";

  var API_URL = "https://structure.timtec.org/api/site-status";
  var REFRESH_MS = 7 * 60 * 1000;

  var DEFAULT_ITEMS = [
    { id: "structure", label: "Structure Search", ok: false, status: "checking" },
    { id: "search", label: "List Search", ok: false, status: "checking" },
    { id: "coa", label: "CoA", ok: false, status: "checking" },
    { id: "sds", label: "SDS", ok: false, status: "checking" },
    { id: "website", label: "Website", ok: false, status: "checking" },
    { id: "portal", label: "Customer portal", ok: false, status: "checking" },
    { id: "collections", label: "Screening Libraries", ok: false, status: "checking" },
  ];

  var items = DEFAULT_ITEMS.map(copyItem);
  var checkedAt = null;
  var root = null;

  function copyItem(item) {
    return {
      id: item.id,
      label: item.label,
      ok: !!item.ok,
      status: item.status || "checking",
    };
  }

  function ledState(item) {
    var status = item && item.status;
    if (item && item.ok && status === "online") return "online";
    if (status === "checking") return "checking";
    return "down";
  }

  function spokenState(state) {
    if (state === "online") return "online";
    if (state === "checking") return "checking";
    return "down";
  }

  function formatCheckedAt(iso) {
    if (!iso) return null;
    try {
      var when = new Date(iso);
      if (isNaN(when.getTime())) return null;
      return when.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    } catch (err) {
      return null;
    }
  }

  function ensureRoot() {
    var existing = document.querySelector("[data-site-status]");
    if (existing) return existing;

    var bar = document.createElement("div");
    bar.className = "site-status-bar";
    bar.setAttribute("data-site-status", "");

    var inner = document.createElement("div");
    inner.className = "wrap site-status-inner";
    bar.appendChild(inner);

    var footer = document.querySelector("footer.site-footer");
    if (footer) {
      footer.appendChild(bar);
    } else if (document.body) {
      document.body.appendChild(bar);
    }
    return bar;
  }

  function render() {
    if (!root) return;
    var inner = root.querySelector(".site-status-inner");
    if (!inner) return;

    inner.innerHTML = "";

    var meta = document.createElement("p");
    meta.className = "site-status-meta";
    var stamp = formatCheckedAt(checkedAt);
    var kicker = document.createElement("span");
    kicker.className = "site-status-kicker";
    kicker.textContent = "System status";
    meta.appendChild(kicker);
    meta.appendChild(document.createTextNode(stamp ? " · " + stamp : " · checking"));
    inner.appendChild(meta);

    var list = document.createElement("ul");
    list.className = "site-status-list";
    list.setAttribute("aria-label", "System status");

    items.forEach(function (item) {
      var state = ledState(item);
      var label = item.label || item.id || "Service";
      var spoken = label + ": " + spokenState(state);

      var li = document.createElement("li");
      var row = document.createElement("span");
      row.className = "site-status-item";
      row.setAttribute("title", spoken);
      row.setAttribute("aria-label", spoken);

      var led = document.createElement("span");
      led.className = "site-status-led";
      led.setAttribute("data-state", state);
      led.setAttribute("aria-hidden", "true");

      var text = document.createElement("span");
      text.textContent = label;

      row.appendChild(led);
      row.appendChild(text);
      li.appendChild(row);
      list.appendChild(li);
    });

    inner.appendChild(list);
  }

  function applyPayload(data) {
    if (!data || !Array.isArray(data.items) || !data.items.length) return;
    items = data.items.map(copyItem);
    checkedAt = data.checkedAt || null;
    render();
  }

  function markCheckingAsDown() {
    items = items.map(function (item) {
      if (item.status === "checking") {
        return { id: item.id, label: item.label, ok: false, status: "error" };
      }
      return item;
    });
    render();
  }

  function refresh() {
    return fetch(API_URL, { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("http_" + res.status);
        return res.json();
      })
      .then(applyPayload)
      .catch(function () {
        markCheckingAsDown();
      });
  }

  function start() {
    if (window.TIMTEC_SITE_STATUS_STARTED) return;
    window.TIMTEC_SITE_STATUS_STARTED = true;
    root = ensureRoot();
    render();
    refresh();
    window.setInterval(refresh, REFRESH_MS);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
