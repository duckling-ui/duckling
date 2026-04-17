# Barrierefreiheit

## Produkt-UI (React)

- Bevorzugen Sie native Steuerelemente oder korrekte ARIA-Rollen (z. B. `role="switch"` + `aria-checked` für Schalter, `role="progressbar"` mit `aria-valuenow` / min / max für Fortschritt).
- Nur-Icon-Schaltflächen brauchen einen zugänglichen Namen (`aria-label`), nicht nur `title`.
- Slide-over-Bereiche, die den Fokus einfangen, nutzen die Semantik von [`useSlideOver`](https://github.com/duckling-ui/duckling/blob/main/frontend/src/hooks/useSlideOver.tsx): `role="dialog"`, `aria-modal="true"`, Escape zum Schließen, Tab-Wrap, Fokus beim Schließen wiederherstellen.
- Formularfelder mit `<label htmlFor>` und `aria-describedby` für Hilfetext verknüpfen.
- `document.documentElement.lang` mit der aktiven Locale synchron halten (siehe `frontend/src/i18n.ts`).
- `prefers-reduced-motion` beachten, wo Animationen dekorativ sind (siehe `frontend/src/index.css` und `useReducedMotion` in Framer Motion, wo verwendet).
- Modale Knoten mit `role="dialog"` sollten einen berechneten zugänglichen Namen haben (`aria-label` mit demselben Text wie der sichtbare Titel wird bei Slide-overs verwendet).
- Lange scrollbare Bereiche nutzen [`ScrollableRegion`](https://github.com/duckling-ui/duckling/blob/main/frontend/src/components/ScrollableRegion.tsx) (`tabIndex={0}`, `role="region"`, `aria-label`), damit Tastaturnutzer den Container fokussieren und scrollen können.

## Dokumentation (MkDocs Material)

- Das Theme liefert Landmarks, Suche und Tastaturnavigation; vermeiden Sie Overrides, die Fokusrahmen entfernen oder den Kontrast ohne triftigen Grund unter WCAG AA senken.
- Abbildungen sollten aussagekräftigen `alt`-Text haben (oder leeren `alt` nur, wenn das Bild rein dekorativ ist und die Bildunterschrift die Bedeutung trägt). Repository-Prüfung: kein nacktes `![](path)` ohne Beschreibung.
- **Karten-Kacheln** (`.card-link`, die eine ganze Feature-Karte auf den lokalisierten Startseiten umschließt): Im öffnenden `<a>` ein explizites **`aria-label`** setzen, das das Ziel nennt (z. B. „Benutzerhandbuch: … Abschnitt“), damit Hilfstechnik nicht auf Emojis/Icons oder horizontale Linien für den Linknamen angewiesen ist. Labels über `docs/index.md`, `docs/es/index.md`, `docs/de/index.md` und `docs/fr/index.md` synchron halten.
- Nach inhaltlichen Theme- oder CSS-Änderungen einen automatisierten Durchlauf auf der **gebauten** Site ausführen (z. B. Lighthouse-Kategorie Barrierefreiheit oder `@axe-core/cli` gegen `site/` nach `mkdocs build`) und Regressionen beheben.
- [`docs/stylesheets/extra.css`](../../stylesheets/extra.css) erhöht den Kontrast gedämpfter Vordergrundfarben im Slate-Schema und unterstreicht Links im Inhalt, damit sie nicht allein über Farbe erkennbar sind.
- [`docs/javascripts/scrollable-focus.js`](../../javascripts/scrollable-focus.js) außerdem: setzt **`aria-label`** auf **`.md-search[role="dialog"]`** (Material-Such-Overlay); verleiht **`nav.md-code__nav`** ein eindeutiges **`aria-label`** pro Codeblock (Kopierleiste); verwendet **aufeinanderfolgende, eindeutige** `aria-label`-Zeichenketten für jede scrollbare Code-/Tabellen-`role="region"` (mit optionaler Bild- oder Tabellenüberschrift); abonniert Materials **`document$`**-Stream, damit diese Korrekturen nach Sofort-Navigation erneut angewendet werden.

## Verwandte Dateien

- Frontend: `frontend/src/components/SettingsPanel.tsx`, `App.tsx` (Header + `BatchProgress`), `ScrollableRegion.tsx`, `DropZone.tsx`, `ConversionProgress.tsx`, `ExportOptions.tsx`, Panel-Komponenten, `frontend/src/hooks/useSlideOver.tsx`, `frontend/src/i18n.ts`, `frontend/src/index.css`, `frontend/tailwind.config.js`.
- Docs: `docs/overrides/main.html`, `docs/stylesheets/extra.css`, `docs/javascripts/scrollable-focus.js`.
