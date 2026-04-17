# Accesibilidad

## Interfaz del producto (React)

- Prefiera controles nativos o roles ARIA correctos (p. ej. `role="switch"` + `aria-checked` para interruptores, `role="progressbar"` con `aria-valuenow` / min / max para el progreso).
- Los botones solo con icono necesitan un nombre accesible (`aria-label`), no solo `title`.
- Los paneles deslizantes que atrapan el foco usan la semántica de [`useSlideOver`](https://github.com/duckling-ui/duckling/blob/main/frontend/src/hooks/useSlideOver.tsx): `role="dialog"`, `aria-modal="true"`, Escape para cerrar, ciclo de Tab, restaurar el foco al cerrar.
- Asocie los campos del formulario con `<label htmlFor>` y `aria-describedby` para el texto de ayuda.
- Mantenga `document.documentElement.lang` alineado con la configuración regional activa (véase `frontend/src/i18n.ts`).
- Respete `prefers-reduced-motion` cuando las animaciones sean decorativas (véase `frontend/src/index.css` y `useReducedMotion` de Framer Motion donde se use).
- Los nodos modales con `role="dialog"` deben tener un nombre accesible calculado (`aria-label` con la misma cadena que el título visible se usa en los paneles deslizantes).
- Las zonas largas con desplazamiento usan [`ScrollableRegion`](https://github.com/duckling-ui/duckling/blob/main/frontend/src/components/ScrollableRegion.tsx) (`tabIndex={0}`, `role="region"`, `aria-label`) para que quienes usan teclado puedan enfocar el contenedor y desplazarse.

## Documentación (MkDocs Material)

- El tema proporciona puntos de referencia, búsqueda y navegación por teclado; evite personalizaciones que quiten los contornos de foco o bajen el contraste por debajo de WCAG AA sin un motivo sólido.
- Las figuras deben incluir texto `alt` significativo (o `alt` vacío solo si la imagen es puramente decorativa y el pie transmite el significado). Comprobación en el repositorio: no `![](path)` sin descripción.
- **Mosaicos de tarjeta** (`.card-link` que envuelve toda una tarjeta de función en las páginas de inicio localizadas): añada un **`aria-label`** explícito en el `<a>` inicial que indique el destino (p. ej. «Guía de usuario: sección …») para que las tecnologías de asistencia no dependan de emojis/iconos ni reglas horizontales para el nombre del enlace. Mantenga las etiquetas sincronizadas entre `docs/index.md`, `docs/es/index.md`, `docs/de/index.md` y `docs/fr/index.md`.
- Tras cambios sustanciales del tema o CSS, ejecute un pase automatizado en el sitio **construido** (p. ej. categoría de accesibilidad de Lighthouse o `@axe-core/cli` sobre `site/` tras `mkdocs build`) y corrija regresiones.
- [`docs/stylesheets/extra.css`](../../stylesheets/extra.css) aumenta el contraste del primer plano atenuado en el esquema slate y subraya los enlaces del contenido para que no se identifiquen solo por el color.
- [`docs/javascripts/scrollable-focus.js`](../../javascripts/scrollable-focus.js) también: establece **`aria-label`** en **`.md-search[role="dialog"]`** (superposición de búsqueda de Material); da a **`nav.md-code__nav`** un **`aria-label`** único por bloque de código (barra de copiar); usa cadenas **`aria-label`** secuenciales y únicas para cada `role="region"` de código/tabla con desplazamiento (con pie de figura / leyenda de tabla opcional); se suscribe al flujo **`document$`** de Material para volver a aplicar estas correcciones tras la navegación instantánea.

## Archivos relacionados

- Frontend: `frontend/src/components/SettingsPanel.tsx`, `App.tsx` (cabecera + `BatchProgress`), `ScrollableRegion.tsx`, `DropZone.tsx`, `ConversionProgress.tsx`, `ExportOptions.tsx`, componentes de panel, `frontend/src/hooks/useSlideOver.tsx`, `frontend/src/i18n.ts`, `frontend/src/index.css`, `frontend/tailwind.config.js`.
- Docs: `docs/overrides/main.html`, `docs/stylesheets/extra.css`, `docs/javascripts/scrollable-focus.js`.
