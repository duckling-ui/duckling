"""Validate screenshot references across all localized documentation."""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DOCS = PROJECT_ROOT / "docs"
ASSETS = DOCS / "assets" / "screenshots"
LOCALES = ("de", "fr", "es")
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
PLACEHOLDER_MARKERS = ("Screenshot Placeholder", "Replace with actual screenshot")
SKIP_DOCS = {
    DOCS / "assets/screenshots/SCREENSHOT_GUIDE.md",
}
SKIP_PREFIXES = (
    DOCS / "docling",
    DOCS / "images",
)


def doc_locale(path: Path) -> str:
    rel = path.relative_to(DOCS)
    if rel.parts and rel.parts[0] in LOCALES:
        return rel.parts[0]
    return "en"


def resolve_ref(doc: Path, ref: str) -> Path | None:
    ref = ref.strip().split()[0].split("#")[0].split("?")[0]
    if ref.startswith(("http://", "https://")):
        return None
    if ref.startswith("/"):
        return DOCS / ref.lstrip("/")
    if ref.startswith("assets/"):
        return DOCS / ref
    return (doc.parent / ref).resolve()


def is_placeholder(path: Path) -> bool:
    if not path.exists():
        return False
    if path.suffix.lower() == ".svg":
        text = path.read_text(encoding="utf-8", errors="ignore")
        return any(marker in text for marker in PLACEHOLDER_MARKERS)
    if path.suffix.lower() == ".png" and path.stat().st_size < 4096:
        return True
    return False


def iter_doc_image_refs():
    for md in sorted(DOCS.rglob("*.md")):
        if md in SKIP_DOCS:
            continue
        if any(str(md).startswith(str(prefix)) for prefix in SKIP_PREFIXES):
            continue
        for match in IMG_RE.finditer(md.read_text(encoding="utf-8")):
            ref = match.group(1).strip().split()[0]
            if "screenshots" not in ref and not ref.endswith("arch.png"):
                continue
            yield md, ref, doc_locale(md)


def test_all_documentation_screenshot_references_exist():
    missing = []
    for doc, ref, _locale in iter_doc_image_refs():
        target = resolve_ref(doc, ref)
        if target is None:
            continue
        if not target.exists():
            missing.append(f"{doc.relative_to(PROJECT_ROOT)} -> {ref} ({target.relative_to(PROJECT_ROOT)})")
    assert not missing, "Missing screenshot assets:\n" + "\n".join(missing)


def test_no_placeholder_screenshots_referenced_in_docs():
    placeholders = []
    for doc, ref, _locale in iter_doc_image_refs():
        target = resolve_ref(doc, ref)
        if target is None or not target.exists():
            continue
        if is_placeholder(target):
            placeholders.append(f"{doc.relative_to(PROJECT_ROOT)} -> {ref}")
    assert not placeholders, "Placeholder screenshots referenced:\n" + "\n".join(placeholders)


def test_localized_docs_use_absolute_asset_paths_for_screenshots():
    bad = []
    for doc, ref, locale in iter_doc_image_refs():
        if locale == "en":
            continue
        if ref.startswith(("http://", "https://")):
            continue
        if not ref.startswith("/assets/") and ref != "/arch.png":
            bad.append(f"{doc.relative_to(PROJECT_ROOT)} -> {ref}")
    assert not bad, "Localized docs must use absolute /assets/ paths:\n" + "\n".join(bad)


def test_localized_docs_prefer_locale_specific_screenshot_assets():
    mismatches = []
    for doc, ref, locale in iter_doc_image_refs():
        if locale == "en" or not ref.startswith("/assets/screenshots/"):
            continue
        rel = ref[len("/assets/screenshots/") :]
        if not rel.endswith(".png"):
            continue
        if rel.endswith(f"-{locale}.png"):
            continue
        candidate = Path(rel).with_name(f"{Path(rel).stem}-{locale}{Path(rel).suffix}")
        candidate_path = ASSETS / candidate
        if candidate_path.exists() and not is_placeholder(candidate_path):
            mismatches.append(
                f"{doc.relative_to(PROJECT_ROOT)} -> {ref} (expected /assets/screenshots/{candidate.as_posix()})"
            )
    assert not mismatches, "Localized docs should use locale-specific PNGs when available:\n" + "\n".join(
        mismatches
    )


def test_preview_assets_are_not_blank():
    preview_files = [
        "export/preview-html-rendered.png",
        "export/preview-html-raw.png",
        "export/preview-markdown-raw.png",
        "export/preview-json.png",
    ]
    for rel in preview_files:
        for locale in ("", "-de", "-fr", "-es"):
            stem = rel.replace(".png", f"{locale}.png")
            path = ASSETS / stem
            if not path.exists():
                continue
            assert path.stat().st_size > 10_000, f"{path} looks blank ({path.stat().st_size} bytes)"


def test_history_panel_assets_are_consistent_size():
    sizes = []
    for locale in ("", "-de", "-fr", "-es"):
        path = ASSETS / f"ui/history-panel{locale}.png"
        if path.exists():
            sizes.append(path.stat().st_size)
    assert sizes, "expected history-panel PNGs"
    assert max(sizes) - min(sizes) < 80_000, f"history-panel sizes vary too much: {sizes}"


def test_architecture_pages_reference_shared_arch_diagram():
    pages = [
        DOCS / "architecture/overview.md",
        DOCS / "de/architecture/overview.md",
        DOCS / "fr/architecture/overview.md",
        DOCS / "es/architecture/overview.md",
    ]
    for page in pages:
        content = page.read_text(encoding="utf-8")
        assert "/arch.png" in content, f"{page} should reference /arch.png"
        assert (DOCS / "arch.png").exists()
