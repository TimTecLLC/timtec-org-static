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

  function setupCustomerGrid() {
    var grid = document.querySelector("[data-customer-grid]");
    if (!grid) return;
    var extras = Array.isArray(window.TIMTEC_EXTRA_CUSTOMERS) ? window.TIMTEC_EXTRA_CUSTOMERS : [];
    extras.forEach(function (item) {
      if (!item || !item.name) return;
      var name = String(item.name).trim();
      if (!name) return;
      var key = name.toLowerCase();
      if (grid.querySelector('[data-customer-name="' + key.replace(/"/g, "") + '"]')) return;
      var cell = document.createElement("div");
      cell.className = "logo-cell text-tile";
      cell.setAttribute("data-customer-name", key);
      cell.setAttribute("data-sort", key);
      var p = document.createElement("p");
      p.className = "org-name";
      p.textContent = name;
      var note = document.createElement("span");
      note.className = "org-note";
      note.textContent = "Name listing";
      cell.appendChild(p);
      cell.appendChild(note);
      grid.appendChild(cell);
    });

    var cells = Array.prototype.slice.call(grid.children);
    cells.sort(function (a, b) {
      return (a.getAttribute("data-sort") || "").localeCompare(b.getAttribute("data-sort") || "", "en", {
        sensitivity: "base",
      });
    });
    cells.forEach(function (cell) {
      grid.appendChild(cell);
    });

    var count = document.querySelector("[data-customer-count]");
    if (count) count.textContent = String(grid.children.length);
  }

  fillBindings();
  setupNav();
  setupForms();
  setupCustomerGrid();
})();
