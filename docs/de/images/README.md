# Screenshots (Deutsch)

Screenshots für die deutschsprachige Dokumentation liegen unter **`docs/assets/screenshots/`** und werden mit absoluten Pfaden referenziert:

```markdown
![Leere Ablagezone](/assets/screenshots/ui/dropzone-empty-de.png)
```

Anleitung: [SCREENSHOT_GUIDE.md](/assets/screenshots/SCREENSHOT_GUIDE.md)

Alle Sprachen neu erzeugen:

```bash
./scripts/capture-screenshots.sh
python3 scripts/normalize_doc_screenshot_paths.py
```
