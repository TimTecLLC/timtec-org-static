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

  var INQUIRY_URL = "https://structure.timtec.org/api/inquiry";
  var MAX_FILE_BYTES = 10 * 1024 * 1024;
  var FILE_EXTS = [".sdf", ".mol", ".smi", ".csv", ".xlsx"];

  function fieldValue(form, name) {
    var el = form.querySelector("[name='" + name + "']");
    if (!el || el.value == null) return "";
    return String(el.value);
  }

  function fileExtension(name) {
    var base = String(name || "").toLowerCase();
    var dot = base.lastIndexOf(".");
    return dot === -1 ? "" : base.slice(dot);
  }

  function selectedFile(form) {
    var input = form.querySelector("input[type='file'][name='file']");
    if (!input || !input.files || !input.files.length) return null;
    return input.files[0];
  }

  function mailtoHref(fields) {
    var lines = ["Name: " + fields.name];
    if (fields.institution) lines.push("Institution: " + fields.institution);
    lines.push("Email: " + fields.email);
    if (fields.phone) lines.push("Phone: " + fields.phone);
    lines.push("Topic: " + fields.topic);
    lines.push("");
    lines.push(fields.message);
    lines.push("");
    lines.push(
      fields.fileName
        ? "A structure file (" + fields.fileName + ") was selected on the website form. Please attach it to this email."
        : "If sending SDF, MOL, SMILES, CSV, or other structure files, attach them to this email with TimTec IDs and required amounts in mg/g."
    );
    var body = lines.join("\n");
    var subject = "TimTec website inquiry — " + (fields.topic || "Inquiry");
    return (
      "mailto:" +
      encodeURIComponent(config.EMAIL || "timtec@timtec.org") +
      "?subject=" +
      encodeURIComponent(subject) +
      "&body=" +
      encodeURIComponent(body)
    );
  }

  function showMailtoFallback(status, href) {
    if (!status) return;
    status.className = "form-status error";
    status.textContent = "";
    status.appendChild(document.createTextNode("The inquiry could not be sent. "));
    var link = document.createElement("a");
    link.href = href;
    link.textContent = "Email timtec@timtec.org";
    status.appendChild(link);
    status.appendChild(document.createTextNode(" instead."));
  }

  function setupForms() {
    document.querySelectorAll("[data-mailto-form]").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var status = form.querySelector("[data-form-status]");
        var button = form.querySelector("button[type='submit']");
        var honey = form.querySelector("[name='website']");
        if (honey && honey.value) {
          return;
        }
        var fields = {
          name: fieldValue(form, "name").trim(),
          institution: fieldValue(form, "institution").trim(),
          email: fieldValue(form, "email").trim(),
          phone: fieldValue(form, "phone").trim(),
          topic: fieldValue(form, "topic").trim() || "Inquiry",
          message: fieldValue(form, "message").trim(),
          website: honey ? honey.value : "",
          fileName: "",
        };
        if (!fields.email) {
          if (status) {
            status.textContent = "Email is required.";
            status.className = "form-status error";
          }
          return;
        }
        if (!fields.name || !fields.message) {
          if (status) {
            status.textContent = "Please complete name, email, and message.";
            status.className = "form-status error";
          }
          return;
        }
        var file = selectedFile(form);
        if (file) {
          var ext = fileExtension(file.name);
          if (FILE_EXTS.indexOf(ext) === -1) {
            if (status) {
              status.textContent = "Attach a .sdf, .mol, .smi, .csv, or .xlsx file.";
              status.className = "form-status error";
            }
            return;
          }
          if (file.size > MAX_FILE_BYTES) {
            if (status) {
              status.textContent = "That file is over 10 MB.";
              status.className = "form-status error";
            }
            return;
          }
          fields.fileName = file.name;
        }

        var href = mailtoHref(fields);
        if (button) button.disabled = true;
        if (status) {
          status.textContent = "Sending…";
          status.className = "form-status";
        }

        var payload;
        var init = { method: "POST" };
        if (file) {
          payload = new FormData();
          payload.append("name", fields.name);
          payload.append("institution", fields.institution);
          payload.append("email", fields.email);
          payload.append("phone", fields.phone);
          payload.append("topic", fields.topic);
          payload.append("message", fields.message);
          payload.append("website", fields.website);
          payload.append("file", file, file.name);
          init.body = payload;
        } else {
          init.headers = { "Content-Type": "application/json" };
          init.body = JSON.stringify({
            name: fields.name,
            institution: fields.institution,
            email: fields.email,
            phone: fields.phone,
            topic: fields.topic,
            message: fields.message,
            website: fields.website,
          });
        }

        fetch(INQUIRY_URL, init)
          .then(function (res) {
            return res.text().then(function (text) {
              var data = null;
              if (text) {
                try {
                  data = JSON.parse(text);
                } catch (err) {
                  data = null;
                }
              }
              if (!res.ok || (data && (data.ok === false || data.error))) {
                throw new Error("inquiry_failed");
              }
            });
          })
          .then(function () {
            if (status) {
              status.textContent = "Inquiry sent.";
              status.className = "form-status ok";
            }
            form.reset();
          })
          .catch(function () {
            showMailtoFallback(status, href);
          })
          .then(function () {
            if (button) button.disabled = false;
          });
      });
    });
  }

  function setupLibraryFinder() {
    var root = document.querySelector("[data-library-finder]");
    if (!root) return;
    var query = root.querySelector("[data-library-query]");
    var empty = root.querySelector("[data-library-empty]");
    var buttons = root.querySelectorAll("[data-library-group]");
    var cards = document.querySelectorAll(".card-grid.libs > article.card");
    var group = "all";

    function groupOf(card) {
      var link = card.querySelector("a[href]");
      var href = link ? link.getAttribute("href") || "" : "";
      if (href.indexOf("actitarg-") !== -1) return "actitarg";
      if (href.indexOf("npl-800") !== -1 || href.indexOf("ndl-3040") !== -1 || href.indexOf("fl-500") !== -1) return "natural";
      if (href.indexOf("/fbl/") !== -1) return "fragments";
      if (href.indexOf("mac-15000") !== -1) return "macrocycles";
      return "diversity";
    }

    function apply() {
      var q = query ? (query.value || "").trim().toLowerCase() : "";
      var shown = 0;
      Array.prototype.forEach.call(cards, function (card) {
        var text = (card.textContent || "").toLowerCase();
        var show = (group === "all" || groupOf(card) === group) && (!q || text.indexOf(q) !== -1);
        card.hidden = !show;
        if (show) shown += 1;
      });
      var actitarg = document.getElementById("actitarg");
      if (actitarg) {
        var visible = actitarg.querySelector("article.card:not([hidden])");
        actitarg.hidden = !visible;
      }
      if (empty) empty.hidden = shown !== 0;
    }

    if (query) {
      query.addEventListener("input", apply);
    }
    Array.prototype.forEach.call(buttons, function (button) {
      button.addEventListener("click", function () {
        group = button.getAttribute("data-library-group") || "all";
        Array.prototype.forEach.call(buttons, function (other) {
          var on = other === button;
          other.classList.toggle("is-on", on);
          other.setAttribute("aria-pressed", on ? "true" : "false");
        });
        apply();
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
    var theme = currentTheme();
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

  function loadHeroParticles() {
    if (window.TIMTEC_PARTICLES_LOADING) return;
    if (!document.querySelector("section.hero, section.page-hero")) return;

    var siteScript = document.querySelector('script[src*="js/site.js"]');
    if (!siteScript) return;

    var src = siteScript.getAttribute("src") || siteScript.src || "";
    var base = src.replace(/[#?].*$/, "").replace(/[^/]+$/, "");
    if (!base) return;

    window.TIMTEC_PARTICLES_LOADING = true;

    function inject(filename, onload) {
      var script = document.createElement("script");
      script.src = base + filename;
      if (onload) script.onload = onload;
      (document.body || document.documentElement).appendChild(script);
    }

    inject("vendor/particles.min.js", function () {
      inject("hero-particles.js");
    });
  }

  function loadSiteStatus() {
    if (window.TIMTEC_SITE_STATUS_LOADING || window.TIMTEC_SITE_STATUS_STARTED) return;

    var siteScript = document.querySelector('script[src*="js/site.js"]');
    if (!siteScript) return;

    var src = siteScript.getAttribute("src") || siteScript.src || "";
    var base = src.replace(/[#?].*$/, "").replace(/[^/]+$/, "");
    if (!base) return;

    window.TIMTEC_SITE_STATUS_LOADING = true;
    var script = document.createElement("script");
    script.src = base + "site-status.js";
    script.defer = true;
    (document.body || document.documentElement).appendChild(script);
  }

  fillBindings();
  applySiteUrls();
  setupThemeChrome();
  setupNav();
  setupForms();
  setupLibraryFinder();
  setupCustomerStrip();
  loadHeroParticles();
  loadSiteStatus();
})();


