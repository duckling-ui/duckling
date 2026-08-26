#!/usr/bin/env python3
"""Normalize screenshot references across localized MkDocs pages."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets" / "screenshots"
LOCALES = ("de", "fr", "es")
IMG_RE = re.compile(r"(!\[[^\]]*\]\()([^)]+)(\))")
PLACEHOLDER_MARKERS = ("Screenshot Placeholder", "Replace with actual screenshot")
SKIP_DOCS = {DOCS / "assets/screenshots/SCREENSHOT_GUIDE.md"}
SKIP_PREFIXES = (DOCS / "docling", DOCS / "images")


def doc_locale(path: Path) -> str:
    rel = path.relative_to(DOCS)
    if rel.parts and rel.parts[0] in LOCALES:
        return rel.parts[0]
    return "en"


def asset_exists(asset_ref: str) -> bool:
    if asset_ref.startswith("/assets/"):
        return (DOCS / asset_ref.lstrip("/")).exists()
    if asset_ref.startswith("assets/"):
        return (DOCS / asset_ref).exists()
    return False


def is_placeholder(path: Path) -> bool:
    if not path.exists():
        return False
    if path.suffix.lower() == ".svg":
        text = path.read_text(encoding="utf-8", errors="ignore")
        return any(marker in text for marker in PLACEHOLDER_MARKERS)
    if path.suffix.lower() == ".png" and path.stat().st_size < 4096:
        return True
    return False


def resolve_relative(doc: Path, ref: str) -> str:
    ref = ref.split("#")[0].split("?")[0].strip()
    if ref.startswith(("http://", "https://")):
        return ref
    resolved = (doc.parent / ref).resolve()
    try:
        rel = resolved.relative_to(DOCS)
    except ValueError:
        return ref
    return f"/{rel.as_posix()}"


def localized_asset(asset_ref: str, locale: str) -> str:
    if locale == "en" or not asset_ref.startswith("/assets/screenshots/"):
        return asset_ref
    rel = asset_ref[len("/assets/screenshots/") :]
    path = Path(rel)
    localized = path.with_name(f"{path.stem}-{locale}{path.suffix}")
    if (ASSETS / localized).exists() and not is_placeholder(ASSETS / localized):
        return f"/assets/screenshots/{localized.as_posix()}"
    return asset_ref


def prefer_png(asset_ref: str, locale: str) -> str:
    asset_ref = localized_asset(asset_ref, locale)
    if not asset_ref.endswith(".svg"):
        return asset_ref
    png_ref = asset_ref[:-4] + ".png"
    png_path = DOCS / png_ref.lstrip("/")
    if png_path.exists() and not is_placeholder(png_path):
        return png_ref
    return asset_ref


def normalize_doc(path: Path) -> bool:
    locale = doc_locale(path)
    original = path.read_text(encoding="utf-8")
    changed = False

    def repl(match: re.Match[str]) -> str:
        nonlocal changed
        prefix, ref, suffix = match.group(1), match.group(2).strip().split()[0], match.group(3)
        if "screenshots" not in ref and not ref.endswith("arch.png"):
            return match.group(0)

        new_ref = resolve_relative(path, ref)
        if ref.endswith("arch.png") or ref.endswith("/arch.png"):
            new_ref = "/arch.png"
        new_ref = prefer_png(new_ref, locale)
        new_ref = localized_asset(new_ref, locale)

        if new_ref != ref:
            changed = True
        return f"{prefix}{new_ref}{suffix}"

    updated = IMG_RE.sub(repl, original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return changed


def main() -> int:
    updated_files = 0
    for md in sorted(DOCS.rglob("*.md")):
        if md in SKIP_DOCS:
            continue
        if any(str(md).startswith(str(prefix)) for prefix in SKIP_PREFIXES):
            continue
        if normalize_doc(md):
            updated_files += 1
            print(f"updated {md.relative_to(ROOT)}")
    print(f"Normalized {updated_files} markdown files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
