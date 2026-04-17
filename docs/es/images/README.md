# Capturas de pantalla (español)

Este directorio contiene capturas para la documentación en español.

## Estructura de carpetas

Organice las capturas en subcarpetas:

- `ui/` — Interfaz principal (zona de entrega, cabecera, historial)
- `settings/` — Panel de configuración
- `export/` — Exportación y vista previa
- `features/` — Funciones (imágenes, tablas, fragmentos, etc.)

## Uso en la documentación

Rutas relativas en Markdown:

```markdown
![Descripción](images/ui/dropzone-empty.png)
```

Desde archivos bajo `es/`:

```markdown
![Descripción](images/ui/dropzone-empty.png)
```

En subcarpetas, ajuste la ruta:

```markdown
![Descripción](../images/ui/dropzone-empty.png)
```

**Importante:** ponga la interfaz en **Español** antes de capturar.

Guía completa: [SCREENSHOT_GUIDE.md](../../assets/screenshots/SCREENSHOT_GUIDE.md).
