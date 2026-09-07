/* TimTec Lab Teal particle field — attaches to every .hero / .page-hero. Respects prefers-reduced-motion. */
(function () {
  "use strict";

  if (window.TIMTEC_PARTICLES_INIT) return;
  if (typeof particlesJS !== "function") return;
  if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  window.TIMTEC_PARTICLES_INIT = true;

  var CONFIG = {
    particles: {
      number: { value: 70, density: { enable: true, value_area: 1000 } },
      color: { value: "#0d9488" },
      shape: { type: "circle", polygon: { nb_sides: 6 } },
      opacity: { value: 0.55, random: false, anim: { enable: false } },
      size: {
        value: 7,
        random: true,
        anim: { enable: true, speed: 6, size_min: 0.4, sync: false }
      },
      line_linked: {
        enable: true,
        distance: 140,
        color: "#0d9488",
        opacity: 0.35,
        width: 1.5
      },
      move: {
        enable: true,
        speed: 1.4,
        direction: "none",
        random: false,
        straight: false,
        out_mode: "out",
        attract: { enable: false, rotateX: 600, rotateY: 1200 }
      }
    },
    interactivity: {
      detect_on: "canvas",
      events: {
        onhover: { enable: true, mode: "repulse" },
        onclick: { enable: true, mode: "repulse" },
        resize: true
      },
      modes: {
        grab: { distance: 400, line_linked: { opacity: 1 } },
        bubble: { distance: 400, size: 28, duration: 2, opacity: 0.6, speed: 3 },
        repulse: { distance: 160 },
        push: { particles_nb: 4 },
        remove: { particles_nb: 2 }
      }
    },
    retina_detect: true
  };

  var heroes = document.querySelectorAll("section.hero, section.page-hero");
  Array.prototype.forEach.call(heroes, function (hero, index) {
    var layer = hero.querySelector(".site-particles, #hero-particles");
    if (!layer) {
      layer = document.createElement("div");
      layer.className = "site-particles";
      layer.id = "site-particles-" + index;
      layer.setAttribute("aria-hidden", "true");
      hero.insertBefore(layer, hero.firstChild);
    } else {
      if (!layer.classList.contains("site-particles")) {
        layer.classList.add("site-particles");
      }
      if (!layer.id) {
        layer.id = "site-particles-" + index;
      }
      layer.setAttribute("aria-hidden", "true");
    }
    particlesJS(layer.id, CONFIG);
  });
})();
