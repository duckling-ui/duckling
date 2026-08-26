# Capturas (Español)

Las capturas de la documentación en español están en **`docs/assets/screenshots/`** y deben referenciarse con rutas absolutas:

```markdown
![Zona vacía](/assets/screenshots/ui/dropzone-empty-es.png)
```

Guía completa: [SCREENSHOT_GUIDE.md](/assets/screenshots/SCREENSHOT_GUIDE.md)

Regenerar todos los idiomas:

```bash
./scripts/capture-screenshots.sh
python3 scripts/normalize_doc_screenshot_paths.py
```
