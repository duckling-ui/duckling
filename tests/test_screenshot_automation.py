"""Tests for Playwright documentation screenshot automation."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "scripts" / "screenshots"
ASSETS_DIR = PROJECT_ROOT / "docs" / "assets" / "screenshots"


def test_screenshot_automation_files_exist():
    required = [
        SCREENSHOTS_DIR / "package.json",
        SCREENSHOTS_DIR / "playwright.config.ts",
        SCREENSHOTS_DIR / "capture.spec.ts",
        SCREENSHOTS_DIR / "mock-api.ts",
        SCREENSHOTS_DIR / "paths.ts",
        SCREENSHOTS_DIR / "config.ts",
        SCREENSHOTS_DIR / "fixtures" / "generate-sample-pdf.py",
        PROJECT_ROOT / "scripts" / "capture-screenshots.sh",
    ]
    for path in required:
        assert path.exists(), f"Missing screenshot automation file: {path}"


def test_frontend_exposes_screenshot_testids():
    app = (PROJECT_ROOT / "frontend/src/App.tsx").read_text(encoding="utf-8")
    dropzone = (PROJECT_ROOT / "frontend/src/components/DropZone.tsx").read_text(encoding="utf-8")
    settings = (PROJECT_ROOT / "frontend/src/components/SettingsPanel.tsx").read_text(encoding="utf-8")
    history = (PROJECT_ROOT / "frontend/src/components/HistoryPanel.tsx").read_text(encoding="utf-8")
    export_options = (PROJECT_ROOT / "frontend/src/components/ExportOptions.tsx").read_text(encoding="utf-8")

    for needle in (
        'data-testid="app-header"',
        'data-testid="open-settings"',
        'data-testid="open-history"',
    ):
        assert needle in app
    assert 'data-testid="dropzone-root"' in dropzone
    assert 'data-testid="dropzone-file-input"' in dropzone
    assert 'data-testid="settings-panel"' in settings
    assert 'data-section="ocr"' in settings or 'sectionId="ocr"' in settings
    assert 'data-testid="history-panel"' in history
    assert 'data-testid="history-panel-search"' in history
    assert 'data-testid={`export-tab-${tab.id}`}' in export_options or 'data-testid="export-tab-images"' in export_options
    assert 'data-testid="export-options"' in export_options


def test_manifest_paths_use_docs_assets_root():
    paths = (SCREENSHOTS_DIR / "paths.ts").read_text(encoding="utf-8")
    assert "docs/assets/screenshots" in paths
    assert "main-english" in paths
    assert "main-german" in paths
    assert "settings-ocr-" in paths or "settings-ocr'" in paths


def test_localized_index_pages_reference_main_screenshots():
    cases = {
        PROJECT_ROOT / "docs/index.md": "/assets/screenshots/ui/main-english.png",
        PROJECT_ROOT / "docs/de/index.md": "/assets/screenshots/ui/main-german.png",
        PROJECT_ROOT / "docs/fr/index.md": "/assets/screenshots/ui/main-french.png",
        PROJECT_ROOT / "docs/es/index.md": "/assets/screenshots/ui/main-spanish.png",
    }
    for path, asset_path in cases.items():
        content = path.read_text(encoding="utf-8")
        assert asset_path in content, f"{path} should reference {asset_path}"
        assert (PROJECT_ROOT / "docs" / asset_path.lstrip("/")).exists()


def test_screenshots_gallery_uses_absolute_asset_paths():
    gallery_pages = [
        PROJECT_ROOT / "docs/user-guide/screenshots.md",
        PROJECT_ROOT / "docs/de/user-guide/screenshots.md",
        PROJECT_ROOT / "docs/fr/user-guide/screenshots.md",
        PROJECT_ROOT / "docs/es/user-guide/screenshots.md",
    ]
    for page in gallery_pages:
        content = page.read_text(encoding="utf-8")
        assert "](/assets/screenshots/" in content, f"{page} should use absolute /assets/ screenshot paths"
        assert "](../assets/screenshots/" not in content, f"{page} still uses fragile relative ../assets paths"
        assert "](../../assets/screenshots/" not in content, f"{page} still uses fragile relative ../../assets paths"


def test_screenshots_gallery_uses_png_for_automated_settings():
    """Settings sections captured by Playwright must not reference SVG placeholders."""
    automated = (
        "settings-tables",
        "settings-images",
        "settings-performance",
        "settings-chunking",
        "settings-output",
    )
    gallery_pages = [
        (PROJECT_ROOT / "docs/user-guide/screenshots.md", ""),
        (PROJECT_ROOT / "docs/de/user-guide/screenshots.md", "-de"),
        (PROJECT_ROOT / "docs/fr/user-guide/screenshots.md", "-fr"),
        (PROJECT_ROOT / "docs/es/user-guide/screenshots.md", "-es"),
    ]
    for page, suffix in gallery_pages:
        content = page.read_text(encoding="utf-8")
        for base in automated:
            png_ref = f"/assets/screenshots/settings/{base}{suffix}.png"
            assert f"{base}.svg" not in content, f"{page} still references placeholder {base}.svg"
            assert png_ref in content, f"{page} should reference {png_ref}"
            assert (PROJECT_ROOT / "docs" / "assets" / "screenshots" / "settings" / f"{base}{suffix}.png").exists()


def test_screenshot_guide_documents_playwright():
    guide = (ASSETS_DIR / "SCREENSHOT_GUIDE.md").read_text(encoding="utf-8")
    assert "Playwright" in guide
    assert "capture-screenshots.sh" in guide
