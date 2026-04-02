# Accessibility

## Product UI (React)

- Prefer native controls or correct ARIA roles (e.g. `role="switch"` + `aria-checked` for toggles, `role="progressbar"` with `aria-valuenow` / min / max for progress).
- Icon-only buttons need an accessible name (`aria-label`), not only `title`.
- Slide-over panels that trap focus use [`useSlideOver`](https://github.com/davidgs/duckling/blob/main/frontend/src/hooks/useSlideOver.tsx) semantics: `role="dialog"`, `aria-modal="true"`, Escape to close, Tab wrap, restore focus on close.
- Associate form fields with `<label htmlFor>` and `aria-describedby` for help text.
- Keep `document.documentElement.lang` in sync with the active locale (see `frontend/src/i18n.ts`).
- Respect `prefers-reduced-motion` where animations are decorative (see `frontend/src/index.css` and `useReducedMotion` in Framer Motion where used).
- Modal `role="dialog"` nodes should have a computed accessible name (`aria-label` with the same string as the visible title is used on slide-overs).
- Long scrollable areas use [`ScrollableRegion`](https://github.com/davidgs/duckling/blob/main/frontend/src/components/ScrollableRegion.tsx) (`tabIndex={0}`, `role="region"`, `aria-label`) so keyboard users can focus the container and scroll.

## Documentation (MkDocs Material)

- Theme provides landmarks, search, and keyboard navigation; avoid overrides that remove focus outlines or drop contrast below WCAG AA without a strong reason.
- Figures should include meaningful `alt` text (or empty `alt` only when the image is purely decorative and the caption carries the meaning). Repository check: no bare `![](path)` without description.
- **Card tiles** (`.card-link` wrapping an entire feature card on the localized home pages): add an explicit **`aria-label`** in the opening `<a>` that states the destination (e.g. “User guide: … section”) so assistive tech does not rely on emoji/icons or horizontal rules for the link name. Keep labels in sync across `docs/index.md`, `docs/es/index.md`, `docs/de/index.md`, and `docs/fr/index.md`.
- After substantive theme or CSS changes, run an automated pass on the **built** site (e.g. Lighthouse accessibility category or `@axe-core/cli` against `site/` after `mkdocs build`) and fix regressions.
- [`docs/stylesheets/extra.css`](../stylesheets/extra.css) bumps muted foreground contrast on the slate scheme and underlines in-content links so they are not identified by color alone.
- [`docs/javascripts/scrollable-focus.js`](../javascripts/scrollable-focus.js) also: sets **`aria-label`** on **`.md-search[role="dialog"]`** (Material search overlay); gives **`nav.md-code__nav`** a unique **`aria-label`** per code block (copy toolbar); uses **sequential, unique** `aria-label` strings for each scrollable code/table `role="region"` (with optional figure caption / table caption); subscribes to Material’s **`document$`** stream so these fixes re-apply after instant navigation.

## Related files

- Frontend: `frontend/src/components/SettingsPanel.tsx`, `App.tsx` (header + `BatchProgress`), `ScrollableRegion.tsx`, `DropZone.tsx`, `ConversionProgress.tsx`, `ExportOptions.tsx`, panel components, `frontend/src/hooks/useSlideOver.tsx`, `frontend/src/i18n.ts`, `frontend/src/index.css`, `frontend/tailwind.config.js`.
- Docs: `docs/overrides/main.html`, `docs/stylesheets/extra.css`, `docs/javascripts/scrollable-focus.js`.
