# English Screenshots

Screenshots for the English documentation live under **`docs/assets/screenshots/`** and are referenced with absolute site-root paths:

```markdown
![Drop zone empty](/assets/screenshots/ui/dropzone-empty.png)
```

See [SCREENSHOT_GUIDE.md](/assets/screenshots/SCREENSHOT_GUIDE.md) for capture instructions and the full manifest.

Regenerate all locales with:

```bash
./scripts/capture-screenshots.sh
python3 scripts/normalize_doc_screenshot_paths.py
```
