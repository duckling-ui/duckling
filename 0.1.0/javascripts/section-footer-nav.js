/**
 * Rewrite MkDocs Material footer Previous/Next links to stay within the
 * currently active top-level nav section.
 *
 * This is primarily to improve navigation in Duckling's in-app docs panel
 * (served under /api/docs/site/<lang>/...), but it also works on the standalone
 * site paths (/es/, /fr/, /de/).
 */

function normalizePathname(pathname) {
  let p = pathname || "/";
  // Drop query/hash (shouldn't be present on pathname, but be defensive)
  p = p.split("?")[0].split("#")[0];
  // Normalize common MkDocs URL variants
  // - /foo/index.html -> /foo/
  // - /foo/index.html/ (defensive) -> /foo/
  p = p.replace(/\/index\.html\/?$/, "/");
  // MkDocs Material uses trailing slashes for directory URLs
  if (!p.endsWith("/")) p = p + "/";
  // Collapse duplicate slashes
  p = p.replace(/\/{2,}/g, "/");
  return p;
}

function isInAppDocsPath(pathname) {
  const p = pathname || "";
  return /^\/api\/docs\/site\/(en|es|fr|de)(\/|$)/.test(p);
}

function getInAppDocsLocale() {
  const m = (window.location.pathname || "").match(/^\/api\/docs\/site\/(en|es|fr|de)(\/|$)/);
  return m ? m[1] : null;
}

function getInAppCurrentDocPath() {
  const lang = getInAppDocsLocale();
  if (!lang) return null;

  // Convert a pathname like:
  // - /api/docs/site/en/                          -> ""
  // - /api/docs/site/en/changelog/               -> "changelog"
  // - /api/docs/site/en/getting-started/install/ -> "getting-started/install"
  let p = window.location.pathname || "";
  p = p.replace(new RegExp(`^/api/docs/site/${lang}`), "");
  p = p.replace(/^\/+/, "");
  p = p.replace(/index\.html$/, "");
  p = p.replace(/\/+$/, "");

  try {
    p = decodeURIComponent(p);
  } catch {
    // ignore decoding errors
  }

  return p;
}

function makeInAppHref(lang, docPath) {
  const trimmed = (docPath || "").replace(/^\/+/, "").replace(/\/+$/, "");
  return trimmed ? `/api/docs/site/${lang}/${trimmed}/` : `/api/docs/site/${lang}/`;
}

function splitDocDisplayName(name) {
  const raw = (name || "").trim();
  const i = raw.indexOf(":");
  if (i === -1) {
    return { category: "__home__", item: raw };
  }
  return {
    category: raw.substring(0, i).trim(),
    item: raw.substring(i + 1).trim(),
  };
}

function getDocsBasePrefix() {
  const p = normalizePathname(window.location.pathname);

  // In-app docs panel: /api/docs/site/<lang>/...
  const m = p.match(/^\/api\/docs\/site\/(en|es|fr|de)\//);
  if (m) return `/api/docs/site/${m[1]}/`;

  // Standalone locale roots: /es/, /fr/, /de/
  const m2 = p.match(/^\/(es|fr|de)\//);
  if (m2) return `/${m2[1]}/`;

  // Default: English at site root
  return "/";
}

function findActiveTopLevelSection() {
  // Primary navigation (left sidebar). We want the active top-level <li>.
  const primaryNav =
    document.querySelector(".md-sidebar--primary nav.md-nav--primary") ||
    document.querySelector("nav.md-nav--primary");
  if (!primaryNav) return null;

  // Avoid :scope (can be flaky in some WebViews).
  const topList = primaryNav.querySelector("ul.md-nav__list");
  if (!topList) return null;

  const topItems = Array.from(topList.children).filter((el) => el && el.tagName === "LI");
  if (!topItems.length) return null;

  // Prefer an active top-level *section*; otherwise any active top-level item.
  const activeSection = topItems.find(
    (li) => li.classList.contains("md-nav__item--active") && li.classList.contains("md-nav__item--section")
  );
  if (activeSection) return activeSection;

  const activeAny = topItems.find((li) => li.classList.contains("md-nav__item--active"));
  return activeAny || null;
}

function collectSectionPages(activeSectionLi) {
  // Collect ordered pages within this top-level section, including the section index.
  // The section index is the section's own anchor (first-level link).
  const pages = [];

  // Avoid :scope selectors. The section index anchor lives inside the top "container".
  const container = activeSectionLi.querySelector(".md-nav__link.md-nav__container");
  const sectionIndexAnchor =
    (container && container.querySelector("a.md-nav__link")) ||
    activeSectionLi.querySelector("a.md-nav__link");
  if (sectionIndexAnchor && sectionIndexAnchor.getAttribute("href")) {
    pages.push({
      anchor: sectionIndexAnchor,
      href: sectionIndexAnchor.getAttribute("href"),
    });
  }

  // Now collect first-level child pages inside this section.
  const childNav = activeSectionLi.querySelector("nav.md-nav[data-md-level='1']");
  if (childNav) {
    const childAnchors = Array.from(
      childNav.querySelectorAll("ul.md-nav__list > li.md-nav__item > a.md-nav__link")
    );

    for (const a of childAnchors) {
      const href = a.getAttribute("href") || "";
      if (!href || href.startsWith("#")) continue;
      pages.push({ anchor: a, href });
    }
  }

  // De-duplicate by resolved pathname while preserving order.
  const seen = new Set();
  const deduped = [];
  for (const p of pages) {
    const resolved = normalizePathname(new URL(p.href, window.location.href).pathname);
    if (seen.has(resolved)) continue;
    seen.add(resolved);
    deduped.push({ ...p, resolvedPathname: resolved });
  }

  return deduped;
}

function setFooterLink(kind, target) {
  const link = document.querySelector(`footer a.md-footer__link--${kind}`);
  if (!link) return;

  if (!target) {
    link.style.display = "none";
    return;
  }

  link.style.display = "";
  link.setAttribute("href", target.resolvedPathname);

  // Update visible label to match target title when possible.
  const titleNode = link.querySelector(".md-footer__title .md-ellipsis");
  if (titleNode) {
    const label = (target.anchor?.textContent || "").trim();
    if (label) titleNode.textContent = label;
  }

  // Update aria-label for assistive tech.
  const label = (target.anchor?.textContent || "").trim();
  if (label) {
    link.setAttribute("aria-label", `${kind === "prev" ? "Previous" : "Next"}: ${label}`);
  }
}

function setFooterLinkRaw(kind, href, label) {
  const link = document.querySelector(`footer a.md-footer__link--${kind}`);
  if (!link) return;

  if (!href) {
    link.style.display = "none";
    return;
  }

  link.style.display = "";
  link.setAttribute("href", href);

  const titleNode = link.querySelector(".md-footer__title .md-ellipsis");
  if (titleNode && label) titleNode.textContent = label;

  if (label) {
    link.setAttribute("aria-label", `${kind === "prev" ? "Previous" : "Next"}: ${label}`);
  }
}

function setHeadRel(kind, target) {
  const rel = kind === "prev" ? "prev" : "next";
  const el = document.querySelector(`head link[rel='${rel}']`);
  if (!el) return;
  if (!target) {
    el.parentNode && el.parentNode.removeChild(el);
    return;
  }
  el.setAttribute("href", target.resolvedPathname);
}

function setHeadRelRaw(kind, href) {
  const rel = kind === "prev" ? "prev" : "next";
  const el = document.querySelector(`head link[rel='${rel}']`);
  if (!el) return;
  if (!href) {
    el.parentNode && el.parentNode.removeChild(el);
    return;
  }
  el.setAttribute("href", href);
}

function updateFooterNavWithinSection() {
  try {
    // basePrefix is kept for future-proofing and sanity checks, but link resolution
    // is done via URL() so this works for both standalone and /api/docs/site/... paths.
    const basePrefix = getDocsBasePrefix();
    const currentPath = normalizePathname(window.location.pathname);

    // If we are in the in-app prefix, keep comparisons within that prefix by using full pathname.
    // (All resolved paths we set will be absolute pathnames.)
    if (!currentPath.startsWith(basePrefix)) {
      // Still proceed; resolution uses URL() anyway.
    }

    const activeSection = findActiveTopLevelSection();
    if (!activeSection) return;

    const sectionPages = collectSectionPages(activeSection);
    if (sectionPages.length < 2) return;

    const idx = sectionPages.findIndex((p) => p.resolvedPathname === currentPath);
    if (idx === -1) return;

    const prev = idx > 0 ? sectionPages[idx - 1] : null;
    const next = idx < sectionPages.length - 1 ? sectionPages[idx + 1] : null;

    setFooterLink("prev", prev);
    setFooterLink("next", next);
    setHeadRel("prev", prev);
    setHeadRel("next", next);
  } catch (e) {
    // Never break page rendering due to navigation enhancement.
    // eslint-disable-next-line no-console
    console.warn("[section-footer-nav] Failed to update footer navigation:", e);
  }
}

let _inAppDocsCache = { lang: null, docs: null, promise: null };

async function getInAppDocsIndex(lang) {
  if (!lang) return null;
  if (_inAppDocsCache.lang === lang && Array.isArray(_inAppDocsCache.docs)) return _inAppDocsCache.docs;
  if (_inAppDocsCache.lang === lang && _inAppDocsCache.promise) return _inAppDocsCache.promise;

  _inAppDocsCache = { lang, docs: null, promise: null };
  _inAppDocsCache.promise = fetch(`/api/docs?lang=${lang}`)
    .then((r) => (r && r.ok ? r.json() : null))
    .then((data) => {
      const docs = data && Array.isArray(data.docs) ? data.docs : null;
      _inAppDocsCache.docs = docs;
      _inAppDocsCache.promise = null;
      return docs;
    })
    .catch(() => {
      _inAppDocsCache.promise = null;
      return null;
    });

  return _inAppDocsCache.promise;
}

async function updateFooterNavWithinInAppCategory() {
  if (!isInAppDocsPath(window.location.pathname)) return false;

  const lang = getInAppDocsLocale();
  if (!lang) return false;

  const currentDocPath = getInAppCurrentDocPath();
  if (currentDocPath === null) return false;

  const docs = await getInAppDocsIndex(lang);
  if (!Array.isArray(docs) || !docs.length) return false;

  const current = docs.find((d) => (d && typeof d.path === "string" ? d.path : "") === currentDocPath) ||
    (currentDocPath === "" ? docs.find((d) => d && d.id === "index") : null);
  if (!current) return false;

  const currentSplit = splitDocDisplayName(current.name);
  const category = currentSplit.category;

  const sameCategory = docs
    .map((d) => {
      const split = splitDocDisplayName(d && d.name);
      return { doc: d, split };
    })
    .filter((x) => x && x.doc && x.split && x.split.category === category)
    .sort((a, b) => (a.split.item || "").localeCompare(b.split.item || ""))
    .map((x) => x.doc);

  if (sameCategory.length < 2) {
    // Still hide navigation if it can't be meaningful.
    setFooterLinkRaw("prev", null, "");
    setFooterLinkRaw("next", null, "");
    setHeadRelRaw("prev", null);
    setHeadRelRaw("next", null);
    return true;
  }

  const idx = sameCategory.findIndex((d) => d && d.id === current.id);
  if (idx === -1) return false;

  const prev = idx > 0 ? sameCategory[idx - 1] : null;
  const next = idx < sameCategory.length - 1 ? sameCategory[idx + 1] : null;

  const prevHref = prev ? makeInAppHref(lang, prev.path) : null;
  const nextHref = next ? makeInAppHref(lang, next.path) : null;
  const prevLabel = prev ? splitDocDisplayName(prev.name).item : "";
  const nextLabel = next ? splitDocDisplayName(next.name).item : "";

  setFooterLinkRaw("prev", prevHref, prevLabel);
  setFooterLinkRaw("next", nextHref, nextLabel);
  setHeadRelRaw("prev", prevHref);
  setHeadRelRaw("next", nextHref);

  return true;
}

function notifyParentOfNavigation() {
  try {
    if (!window.parent || window.parent === window) return;
    const origin = window.location.origin || "*";
    window.parent.postMessage(
      { type: "duckling-docs:navigate", pathname: window.location.pathname },
      origin
    );
  } catch {
    // ignore
  }
}

async function updateFooterNav() {
  const inApp = isInAppDocsPath(window.location.pathname);
  if (inApp) {
    const ok = await updateFooterNavWithinInAppCategory();
    if (!ok) updateFooterNavWithinSection();
    notifyParentOfNavigation();
    return;
  }

  updateFooterNavWithinSection();
}

// Run once on initial load.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => void updateFooterNav());
} else {
  void updateFooterNav();
}

// Support Material for MkDocs instant navigation (navigation.instant).
if (typeof window.document$ !== "undefined" && window.document$ && typeof window.document$.subscribe === "function") {
  window.document$.subscribe(() => void updateFooterNav());
}

// Also broadcast navigation changes (instant navigation updates the URL without a full reload).
if (typeof window.location$ !== "undefined" && window.location$ && typeof window.location$.subscribe === "function") {
  window.location$.subscribe(notifyParentOfNavigation);
}

