/**
 * Apply the selected visual theme before first paint.
 * Default is Lab Teal. ?theme= writes localStorage unless preview=1 (gallery iframes).
 */
(function () {
  "use strict";
  var KEY = "timtec-theme";
  var ALLOWED = {
    classic: true,
    "lab-teal": true,
    "pharma-navy": true,
    "clean-air": true,
  };
  var params;
  try {
    params = new URLSearchParams(window.location.search);
  } catch (err) {
    params = null;
  }
  var query = params ? params.get("theme") : null;
  var preview = params ? params.get("preview") === "1" : false;
  var stored = null;
  try {
    stored = window.localStorage.getItem(KEY);
  } catch (err) {
    stored = null;
  }
  var theme = ALLOWED[query] ? query : ALLOWED[stored] ? stored : "lab-teal";
  if (ALLOWED[query] && !preview) {
    try {
      window.localStorage.setItem(KEY, query);
    } catch (err) {
      /* ignore quota / private mode */
    }
  }
  document.documentElement.setAttribute("data-theme", theme);
  var colors = {
    classic: "#132a7a",
    "lab-teal": "#0d4f4b",
    "pharma-navy": "#0c1228",
    "clean-air": "#0b4f8a",
  };
  var meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute("content", colors[theme] || colors["lab-teal"]);
})();
