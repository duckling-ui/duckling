# Spanish Screenshots (Español)

This directory contains screenshots for the Spanish locale documentation.

## Directory Structure

Organize screenshots into subdirectories:

- `ui/` - Main interface screenshots (dropzone, header, history)
- `settings/` - Settings panel screenshots
- `export/` - Export options and preview screenshots
- `features/` - Feature-specific screenshots (images, tables, chunks, etc.)

## Usage in Documentation

Reference screenshots from markdown files using relative paths:

```markdown
![Description](images/ui/dropzone-empty.png)
```

For files in the `es/` directory, use:
```markdown
![Description](images/ui/dropzone-empty.png)
```

For files in subdirectories, adjust the path accordingly:
```markdown
![Description](../images/ui/dropzone-empty.png)
```

**Important**: Ensure the UI language is set to Español before capturing screenshots.

See [SCREENSHOT_GUIDE.md](../../assets/screenshots/SCREENSHOT_GUIDE.md) for complete capture instructions.
