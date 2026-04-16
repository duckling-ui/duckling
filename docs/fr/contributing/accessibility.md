# Accessibilité

## Interface produit (React)

- Privilégier les contrôles natifs ou les rôles ARIA corrects (par ex. `role="switch"` + `aria-checked` pour les bascules, `role="progressbar"` avec `aria-valuenow` / min / max pour la progression).
- Les boutons uniquement iconographiques ont besoin d’un nom accessible (`aria-label`), pas seulement de `title`.
- Les panneaux coulissants qui piègent le focus utilisent la sémantique de [`useSlideOver`](https://github.com/duckling-ui/duckling/blob/main/frontend/src/hooks/useSlideOver.tsx) : `role="dialog"`, `aria-modal="true"`, Échap pour fermer, boucle Tab, restauration du focus à la fermeture.
- Associer les champs de formulaire avec `<label htmlFor>` et `aria-describedby` pour le texte d’aide.
- Garder `document.documentElement.lang` aligné sur la locale active (voir `frontend/src/i18n.ts`).
- Respecter `prefers-reduced-motion` lorsque les animations sont décoratives (voir `frontend/src/index.css` et `useReducedMotion` dans Framer Motion le cas échéant).
- Les nœuds modaux `role="dialog"` doivent avoir un nom accessible calculé (`aria-label` avec la même chaîne que le titre visible est utilisé sur les panneaux coulissants).
- Les zones longues défilantes utilisent [`ScrollableRegion`](https://github.com/duckling-ui/duckling/blob/main/frontend/src/components/ScrollableRegion.tsx) (`tabIndex={0}`, `role="region"`, `aria-label`) pour que les utilisateurs au clavier puissent focaliser le conteneur et faire défiler.

## Documentation (MkDocs Material)

- Le thème fournit repères, recherche et navigation clavier ; évitez les surcharges qui suppriment les contours de focus ou abaissent le contraste sous WCAG AA sans raison forte.
- Les figures doivent avoir un texte `alt` pertinent (ou `alt` vide uniquement si l’image est purement décorative et que la légende porte le sens). Vérification dépôt : pas de `![](path)` nu sans description.
- **Tuiles de carte** (`.card-link` englobant une carte entière sur les pages d’accueil localisées) : ajoutez un **`aria-label`** explicite sur le `<a>` d’ouverture indiquant la destination (par ex. « Guide utilisateur : section … ») pour que les technologies d’assistance ne dépendent pas des émojis/icônes ni des séparateurs horizontaux pour le nom du lien. Gardez les libellés synchronisés entre `docs/index.md`, `docs/es/index.md`, `docs/de/index.md` et `docs/fr/index.md`.
- Après des changements substantiels de thème ou CSS, lancez un passage automatisé sur le site **construit** (par ex. catégorie accessibilité Lighthouse ou `@axe-core/cli` sur `site/` après `mkdocs build`) et corrigez les régressions.
- [`docs/stylesheets/extra.css`](../../stylesheets/extra.css) augmente le contraste du texte atténué sur le schéma slate et souligne les liens dans le contenu pour qu’ils ne soient pas identifiés par la couleur seule.
- [`docs/javascripts/scrollable-focus.js`](../../javascripts/scrollable-focus.js) également : définit un **`aria-label`** sur **`.md-search[role="dialog"]`** (overlay de recherche Material) ; donne à **`nav.md-code__nav`** un **`aria-label`** unique par bloc de code (barre de copie) ; utilise des chaînes **`aria-label`** séquentielles et uniques pour chaque `role="region"` de code/tableau défilable (avec légende de figure / légende de tableau optionnelle) ; s’abonne au flux **`document$`** de Material pour réappliquer ces correctifs après navigation instantanée.

## Fichiers connexes

- Frontend : `frontend/src/components/SettingsPanel.tsx`, `App.tsx` (en-tête + `BatchProgress`), `ScrollableRegion.tsx`, `DropZone.tsx`, `ConversionProgress.tsx`, `ExportOptions.tsx`, composants de panneau, `frontend/src/hooks/useSlideOver.tsx`, `frontend/src/i18n.ts`, `frontend/src/index.css`, `frontend/tailwind.config.js`.
- Docs : `docs/overrides/main.html`, `docs/stylesheets/extra.css`, `docs/javascripts/scrollable-focus.js`.
