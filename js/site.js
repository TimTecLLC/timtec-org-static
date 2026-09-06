(function () {
  "use strict";

  var config = window.SITE_CONFIG || {};

  function text(value, fallback) {
    if (value == null) return fallback || "";
    var filled = String(value).trim();
    return filled || fallback || "";
  }

  function telHref(value) {
    var digits = String(value || "").replace(/[^\d]/g, "");
    if (digits.length === 10) return "tel:+1" + digits;
    if (digits.length === 11 && digits.charAt(0) === "1") return "tel:+" + digits;
    return "tel:" + digits;
  }

  function fillBindings() {
    document.querySelectorAll("[data-bind]").forEach(function (el) {
      var key = el.getAttribute("data-bind");
      var filled = text(config[key], el.getAttribute("data-fallback") || "");
      if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
        el.value = filled;
        return;
      }
      el.textContent = filled;
    });

    document.querySelectorAll("[data-bind-href]").forEach(function (el) {
      var key = el.getAttribute("data-bind-href");
      var value = config[key];
      if (!value) return;
      var prefix = el.getAttribute("data-href-prefix") || "";
      if (prefix === "tel:") {
        el.setAttribute("href", telHref(value));
      } else if (prefix === "mailto:") {
        el.setAttribute("href", "mailto:" + String(value).trim());
      } else {
        el.setAttribute("href", prefix + String(value).trim());
      }
    });

    document.querySelectorAll("[data-year]").forEach(function (el) {
      el.textContent = String(new Date().getFullYear());
    });
  }

  function setupNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var nav = document.querySelector("[data-site-nav]");
    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        var open = nav.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
    }

    document.querySelectorAll("[data-dropdown]").forEach(function (item) {
      var button = item.querySelector("button.has-sub");
      if (!button) return;
      button.addEventListener("click", function (event) {
        event.preventDefault();
        var willOpen = !item.classList.contains("is-open");
        document.querySelectorAll("[data-dropdown].is-open").forEach(function (other) {
          if (other !== item) other.classList.remove("is-open");
        });
        item.classList.toggle("is-open", willOpen);
        button.setAttribute("aria-expanded", willOpen ? "true" : "false");
      });
    });

    document.addEventListener("click", function (event) {
      if (event.target.closest("[data-dropdown]") || event.target.closest("[data-nav-toggle]")) {
        return;
      }
      document.querySelectorAll("[data-dropdown].is-open").forEach(function (item) {
        item.classList.remove("is-open");
        var button = item.querySelector("button.has-sub");
        if (button) button.setAttribute("aria-expanded", "false");
      });
    });
  }

  function setupForms() {
    document.querySelectorAll("[data-mailto-form]").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var status = form.querySelector("[data-form-status]");
        var honey = form.querySelector("[name='website']");
        if (honey && honey.value) {
          return;
        }
        var name = (form.querySelector("[name='name']") || {}).value || "";
        var email = (form.querySelector("[name='email']") || {}).value || "";
        var phone = (form.querySelector("[name='phone']") || {}).value || "";
        var topic = (form.querySelector("[name='topic']") || {}).value || "Inquiry";
        var message = (form.querySelector("[name='message']") || {}).value || "";
        if (!name.trim() || !email.trim() || !message.trim()) {
          if (status) {
            status.textContent = "Please complete name, email, and message.";
            status.className = "form-status error";
          }
          return;
        }
        var body = [
          "Name: " + name.trim(),
          "Email: " + email.trim(),
          phone.trim() ? "Phone: " + phone.trim() : "",
          "Topic: " + topic,
          "",
          message.trim(),
          "",
          "If sending SDF, MOL, SMILES, or other structure files, attach them to this email with TimTec IDs and required amounts in mg/g.",
        ]
          .filter(function (line, idx, arr) {
            return line !== "" || (idx > 0 && arr[idx - 1] !== "");
          })
          .join("\n");
        var subject = "TimTec website inquiry — " + topic;
        var href =
          "mailto:" +
          encodeURIComponent(config.EMAIL || "timtec@timtec.org") +
          "?subject=" +
          encodeURIComponent(subject) +
          "&body=" +
          encodeURIComponent(body);
        if (status) {
          status.textContent = "Opening your email app…";
          status.className = "form-status ok";
        }
        window.location.href = href;
      });
    });
  }

  function setupCustomerStrip() {
    var group = document.querySelector("[data-customer-group]");
    var track = document.querySelector("[data-customer-track]");
    var strip = document.querySelector("[data-customer-strip]");
    if (!group) return;

    var extras = Array.isArray(window.TIMTEC_EXTRA_CUSTOMERS) ? window.TIMTEC_EXTRA_CUSTOMERS : [];
    extras.forEach(function (item) {
      if (!item || !item.name) return;
      var name = String(item.name).trim();
      if (!name) return;
      if (/^(molport|mcule)$/i.test(name)) return;
      var key = name.toLowerCase();
      var already = Array.prototype.some.call(group.querySelectorAll("[data-customer-name]"), function (el) {
        return (el.getAttribute("data-customer-name") || "").toLowerCase() === key;
      });
      if (already) return;
      var cell = document.createElement("li");
      cell.className = "logo-cell text-tile";
      cell.setAttribute("data-customer-name", key);
      cell.setAttribute("data-sort", key);
      var label = document.createElement("span");
      label.className = "org-name";
      label.textContent = name;
      cell.appendChild(label);
      group.appendChild(cell);
    });

    Array.prototype.forEach.call(group.querySelectorAll(".logo-cell"), function (cell) {
      if (cell.querySelector("img")) {
        cell.classList.remove("text-tile");
        Array.prototype.forEach.call(cell.querySelectorAll(".org-name"), function (label) {
          label.parentNode.removeChild(label);
        });
      }
    });

    var cells = Array.prototype.slice.call(group.children);
    cells.sort(function (a, b) {
      return (a.getAttribute("data-sort") || "").localeCompare(b.getAttribute("data-sort") || "", "en", {
        sensitivity: "base",
      });
    });
    cells.forEach(function (cell) {
      group.appendChild(cell);
    });

    var index = document.querySelector("[data-customer-index]");
    if (index) {
      index.innerHTML = "";
      cells.forEach(function (cell) {
        var li = document.createElement("li");
        var nameEl = cell.querySelector(".org-name");
        var img = cell.querySelector("img");
        li.textContent = (nameEl && nameEl.textContent) || (img && (img.getAttribute("alt") || img.getAttribute("title"))) || "";
        if (li.textContent) index.appendChild(li);
      });
    }

    if (track && strip && cells.length) {
      var clone = group.cloneNode(true);
      clone.removeAttribute("data-customer-group");
      clone.setAttribute("aria-hidden", "true");
      track.appendChild(clone);
      strip.style.setProperty("--strip-duration", "120s");
      function setPaused(paused) {
        track.style.animationPlayState = paused ? "paused" : "running";
        strip.classList.toggle("is-paused", paused);
      }
      strip.addEventListener("pointerenter", function () {
        setPaused(true);
      });
      strip.addEventListener("pointerleave", function () {
        setPaused(false);
      });
    }
  }

  function siteRoot() {
    var link = document.querySelector('link[rel="stylesheet"][href*="css/styles.css"]');
    if (!link) return "";
    return String(link.getAttribute("href") || "").replace(/css\/styles\.css.*$/, "");
  }

  function normalizeSiteUrl(url) {
    return String(url || "").replace(/\/$/, "");
  }

  function pagePath() {
    var pathname = "/";
    try {
      pathname = window.location.pathname || "/";
    } catch (err) {
      pathname = "/";
    }
    var previewPrefix = "/timtec-org-static";
    if (pathname === previewPrefix || pathname.indexOf(previewPrefix + "/") === 0) {
      pathname = pathname.slice(previewPrefix.length) || "/";
    }
    if (!pathname || pathname.charAt(0) !== "/") {
      pathname = "/" + pathname;
    }
    if (/\/index\.html$/i.test(pathname)) {
      pathname = pathname.replace(/\/index\.html$/i, "/");
    }
    if (/\/404\.html$/i.test(pathname)) {
      pathname = "/";
    }
    if (pathname !== "/" && pathname.indexOf(".") === -1 && pathname.charAt(pathname.length - 1) !== "/") {
      pathname += "/";
    }
    return pathname || "/";
  }

  function applySiteUrls() {
    var siteUrl = normalizeSiteUrl(config.SITE_URL || config.PRODUCTION_URL || "https://www.timtec.org");
    var path = pagePath();
    var pageUrl = siteUrl + (path === "/" ? "/" : path);
    var logoUrl = siteUrl + "/assets/logo.jpg";

    var canonical = document.querySelector('link[rel="canonical"]');
    if (canonical) {
      var existing = canonical.getAttribute("href") || "";
      var query = "";
      var qIndex = existing.indexOf("?");
      if (qIndex !== -1) {
        query = existing.slice(qIndex);
        canonical.setAttribute("href", siteUrl + "/" + query);
      } else {
        canonical.setAttribute("href", pageUrl);
      }
    }

    var ogUrl = document.querySelector('meta[property="og:url"]');
    if (!ogUrl) {
      ogUrl = document.createElement("meta");
      ogUrl.setAttribute("property", "og:url");
      var after = document.querySelector('meta[property="og:type"]') || canonical;
      if (after && after.parentNode) {
        after.parentNode.insertBefore(ogUrl, after.nextSibling);
      } else if (document.head) {
        document.head.appendChild(ogUrl);
      }
    }
    if (ogUrl) {
      ogUrl.setAttribute("content", (canonical && canonical.getAttribute("href")) || pageUrl);
    }

    var ogImage = document.querySelector('meta[property="og:image"]');
    if (ogImage) {
      ogImage.setAttribute("content", logoUrl);
    }

    document.querySelectorAll('script[type="application/ld+json"]').forEach(function (script) {
      try {
        var data = JSON.parse(script.textContent);
        if (!data || typeof data !== "object") return;
        if (data.url) data.url = siteUrl + "/";
        if (data.logo) data.logo = logoUrl;
        script.textContent = JSON.stringify(data);
      } catch (err) {
        /* leave static JSON-LD */
      }
    });
  }

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") || "lab-teal";
  }

  function setupThemeChrome() {
    var root = siteRoot();
    var labels = {
      classic: "Classic",
      "lab-teal": "Lab Teal",
      "pharma-navy": "Pharma Navy",
      "clean-air": "Clean Air",
    };
    var theme = currentTheme();
    var headerInner = document.querySelector(".header-inner");
    if (headerInner && !document.querySelector(".design-chip")) {
      var chip = document.createElement("a");
      chip.className = "design-chip";
      chip.href = root + "themes/";
      chip.setAttribute("data-design-chip", "");
      chip.innerHTML =
        "<span>Design previews</span><span class=\"design-chip-theme\">" +
        (labels[theme] || "Classic") +
        "</span>";
      var toggle = headerInner.querySelector("[data-nav-toggle]");
      if (toggle) headerInner.insertBefore(chip, toggle);
      else headerInner.appendChild(chip);
    }

    var siteList = document.querySelector(".site-footer .footer-grid div:nth-child(3) ul");
    if (siteList && !siteList.querySelector("[data-theme-gallery]")) {
      var item = document.createElement("li");
      var link = document.createElement("a");
      link.setAttribute("data-theme-gallery", "");
      link.href = root + "themes/";
      link.textContent = "Theme gallery";
      item.appendChild(link);
      siteList.appendChild(item);
    }

    document.querySelectorAll("[data-theme-set]").forEach(function (el) {
      var id = el.getAttribute("data-theme-set");
      if (id === theme) {
        el.classList.add("is-current");
        el.setAttribute("aria-current", "true");
      }
      el.addEventListener("click", function () {
        try {
          window.localStorage.setItem("timtec-theme-v2", id);
        } catch (err) {
          /* ignore */
        }
      });
    });
  }

  fillBindings();
  applySiteUrls();
  setupThemeChrome();
  setupNav();
  setupForms();
  setupCustomerStrip();
})();

