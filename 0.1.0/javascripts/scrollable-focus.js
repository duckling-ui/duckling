/**
 * MkDocs Material accessibility extras:
 * - Search overlay (role="dialog") gets an accessible name.
 * - Scrollable code blocks and tables: focusable + unique region labels.
 * - Code "copy" toolbar nav: unique aria-label per block.
 */
(function () {
  var STR = {
    en: {
      siteSearch: "Site search",
      codeActions: "Code block {n} — toolbar (copy to clipboard)",
      codeRegion: "Code block {n} (scroll horizontally if needed)",
      codeRegionCaption: "{caption} — code block {n}",
      tableRegion: "Data table {n} (scroll horizontally if needed)",
      tableRegionCaption: "{caption} — table {n}",
    },
    es: {
      siteSearch: "Búsqueda en el sitio",
      codeActions: "Bloque de código {n} — barra de acciones (copiar al portapapeles)",
      codeRegion: "Bloque de código {n} (desplazar horizontalmente si hace falta)",
      codeRegionCaption: "{caption} — bloque de código {n}",
      tableRegion: "Tabla de datos {n} (desplazar horizontalmente si hace falta)",
      tableRegionCaption: "{caption} — tabla {n}",
    },
    de: {
      siteSearch: "Websuche",
      codeActions: "Codeblock {n} — Aktionen (in die Zwischenablage kopieren)",
      codeRegion: "Codeblock {n} (bei Bedarf horizontal scrollen)",
      codeRegionCaption: "{caption} — Codeblock {n}",
      tableRegion: "Datentabelle {n} (bei Bedarf horizontal scrollen)",
      tableRegionCaption: "{caption} — Tabelle {n}",
    },
    fr: {
      siteSearch: "Recherche sur le site",
      codeActions: "Bloc de code {n} — barre d’actions (copier dans le presse-papiers)",
      codeRegion: "Bloc de code {n} (faites défiler horizontalement si besoin)",
      codeRegionCaption: "{caption} — bloc de code {n}",
      tableRegion: "Tableau de données {n} (faites défiler horizontalement si besoin)",
      tableRegionCaption: "{caption} — tableau {n}",
    },
  };

  function locale() {
    var l = (document.documentElement.getAttribute("lang") || "en").toLowerCase();
    var base = l.split("-")[0];
    return STR[base] ? base : "en";
  }

  function txt(key, replacements) {
    var bundle = STR[locale()] || STR.en;
    var s = bundle[key] || STR.en[key] || key;
    if (replacements) {
      Object.keys(replacements).forEach(function (k) {
        s = s.split("{" + k + "}").join(replacements[k]);
      });
    }
    return s;
  }

  function labelFromFigure(el) {
    var fig = el.closest("figure");
    if (fig) {
      var cap = fig.querySelector("figcaption");
      if (cap && cap.textContent.trim()) {
        return cap.textContent.trim();
      }
    }
    return null;
  }

  function tableCaptionFromWrapper(el) {
    var table = el.querySelector("table");
    if (!table) return null;
    var cap = table.querySelector("caption");
    if (cap && cap.textContent.trim()) return cap.textContent.trim();
    return null;
  }

  function enhanceSearchDialog() {
    document.querySelectorAll('.md-search[role="dialog"]').forEach(function (el) {
      if (el.getAttribute("aria-labelledby") || el.getAttribute("aria-label")) {
        return;
      }
      el.setAttribute("aria-label", txt("siteSearch"));
    });
  }

  function enhanceCodeNav() {
    document.querySelectorAll(".md-code__nav").forEach(function (nav, idx) {
      if (nav.getAttribute("aria-label")) return;
      nav.setAttribute("aria-label", txt("codeActions", { n: String(idx + 1) }));
    });
  }

  function enhanceHighlights() {
    var n = 0;
    document.querySelectorAll(".md-typeset .highlight").forEach(function (el) {
      if (el.getAttribute("tabindex") !== null) return;
      n += 1;
      el.setAttribute("tabindex", "0");
      el.setAttribute("role", "region");
      var cap = labelFromFigure(el);
      var label = cap
        ? txt("codeRegionCaption", { caption: cap, n: String(n) })
        : txt("codeRegion", { n: String(n) });
      el.setAttribute("aria-label", label);
    });
  }

  function enhanceTables() {
    var n = 0;
    document.querySelectorAll(".md-typeset__table").forEach(function (el) {
      if (el.getAttribute("tabindex") !== null) return;
      n += 1;
      el.setAttribute("tabindex", "0");
      el.setAttribute("role", "region");
      var cap = tableCaptionFromWrapper(el);
      var label = cap
        ? txt("tableRegionCaption", { caption: cap, n: String(n) })
        : txt("tableRegion", { n: String(n) });
      el.setAttribute("aria-label", label);
    });
  }

  function enhance() {
    enhanceSearchDialog();
    enhanceCodeNav();
    enhanceHighlights();
    enhanceTables();
  }

  var instantNavSubscribed = false;

  function subscribeInstantNav() {
    if (instantNavSubscribed) return;
    var bus =
      (typeof document$ !== "undefined" && document$) ||
      (typeof window !== "undefined" && window.document$);
    if (bus && typeof bus.subscribe === "function") {
      bus.subscribe(enhance);
      instantNavSubscribed = true;
    }
  }

  function setup() {
    enhance();
    subscribeInstantNav();
    if (!instantNavSubscribed) {
      setTimeout(subscribeInstantNav, 0);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }
})();
