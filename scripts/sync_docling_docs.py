#!/usr/bin/env python3
"""
Sync a curated subset of upstream Docling docs into this repository.

This intentionally vendors only a small set of markdown pages that render well
in our MkDocs setup (no upstream-only plugins required).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable


UPSTREAM_REPO = "docling-project/docling"
UPSTREAM_SITE = "https://docling-project.github.io/docling/"

# local_relative_path -> upstream_repo_path (relative to repo root)
DOC_MAP: dict[str, str] = {
    "docs/docling/installation.md": "docs/getting_started/installation.md",
    "docs/docling/quickstart.md": "docs/getting_started/quickstart.md",
    "docs/docling/supported-formats.md": "docs/usage/supported_formats.md",
    "docs/docling/advanced-options.md": "docs/usage/advanced_options.md",
    "docs/docling/architecture.md": "docs/concepts/architecture.md",
    "docs/docling/docling-document.md": "docs/concepts/docling_document.md",
}

PAGE_TITLES: dict[str, str] = {
    "docs/docling/installation.md": "Installation (Docling)",
    "docs/docling/quickstart.md": "Quickstart (Docling)",
    "docs/docling/supported-formats.md": "Supported formats (Docling)",
    "docs/docling/advanced-options.md": "Advanced options (Docling)",
    "docs/docling/architecture.md": "Architecture (Docling)",
    "docs/docling/docling-document.md": "DoclingDocument (Docling)",
}


def fetch_text(url: str, timeout_s: int = 30) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "duckling-ui sync_docling_docs.py",
            "Accept": "text/plain; charset=utf-8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return resp.read().decode("utf-8", "replace")


def try_get_upstream_commit_sha(branch: str, timeout_s: int = 30) -> str | None:
    """Best-effort SHA lookup; returns None if unavailable."""
    api_url = f"https://api.github.com/repos/{UPSTREAM_REPO}/commits/{branch}"
    try:
        data = fetch_text(api_url, timeout_s=timeout_s)
        payload = json.loads(data)
        sha = payload.get("sha")
        if isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{7,40}", sha):
            return sha
    except (urllib.error.URLError, json.JSONDecodeError, ValueError):
        return None
    return None


def apply_rewrites(text: str) -> str:
    # Normalize newlines first.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    replacements = {
        # Images: keep external (we don't vendor binaries).
        "../assets/docling_arch.png": f"{UPSTREAM_SITE}assets/docling_arch.png",
        "../assets/docling_doc_hierarchy_1.png": f"{UPSTREAM_SITE}assets/docling_doc_hierarchy_1.png",
        "../assets/docling_doc_hierarchy_2.png": f"{UPSTREAM_SITE}assets/docling_doc_hierarchy_2.png",
        # Cross-links to vendored pages.
        "../usage/supported_formats.md": "supported-formats.md",
        "../concepts/architecture.md": "architecture.md",
        "../concepts/docling_document.md": "docling-document.md",
        "./docling_document.md": "docling-document.md",
        # Cross-links to upstream docs (not vendored).
        "../reference/cli.md": f"{UPSTREAM_SITE}reference/cli/",
        "../examples/index.md": f"{UPSTREAM_SITE}examples/",
        "./serialization.md": f"{UPSTREAM_SITE}concepts/serialization/",
        "./chunking.md": f"{UPSTREAM_SITE}concepts/chunking/",
        # Architecture page points to usage index; closest vendored match:
        "../usage/index.md#adjust-pipeline-features": "advanced-options.md#adjust-pipeline-features",
        # Advanced options references an example file rendered via mkdocs-jupyter upstream.
        "../examples/custom_convert.py": f"https://github.com/{UPSTREAM_REPO}/blob/main/docs/examples/custom_convert.py",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def wrap_with_header(*, title: str, upstream_path: str, upstream_ref: str, upstream_sha: str | None, body: str) -> str:
    sha_line = f"    Upstream ref: `{upstream_sha[:12]}`\n" if upstream_sha else ""
    return (
        f"# {title}\n\n"
        f'!!! note "Vendored from upstream Docling"\n'
        f"    Source: `{UPSTREAM_REPO}` (`{upstream_path}`, ref `{upstream_ref}`).\n"
        f"{sha_line}"
        f"\n"
        f"    For the full upstream docs, see `{UPSTREAM_SITE}`.\n\n"
        f"{body.rstrip()}\n"
    )


def iter_targets(repo_root: Path) -> Iterable[tuple[Path, str, str]]:
    for local_rel, upstream_path in DOC_MAP.items():
        yield (repo_root / local_rel, local_rel, upstream_path)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Sync a curated subset of Docling docs into docs/docling/")
    parser.add_argument("--branch", default="main", help="Upstream branch/ref to fetch (default: main)")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and rewrite, but do not write files")
    parser.add_argument("--verbose", action="store_true", help="Print per-file actions")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    upstream_sha = try_get_upstream_commit_sha(args.branch)

    for local_path, local_rel, upstream_path in iter_targets(repo_root):
        raw_url = f"https://raw.githubusercontent.com/{UPSTREAM_REPO}/{args.branch}/{upstream_path}"
        if args.verbose:
            print(f"[sync] fetch {upstream_path} -> {local_rel}")

        try:
            upstream_text = fetch_text(raw_url)
        except urllib.error.URLError as e:
            print(f"[sync] ERROR fetching {raw_url}: {e}", file=sys.stderr)
            return 1

        rewritten = apply_rewrites(upstream_text)
        title = PAGE_TITLES.get(local_rel, local_path.stem)
        final_text = wrap_with_header(
            title=title,
            upstream_path=upstream_path,
            upstream_ref=args.branch,
            upstream_sha=upstream_sha,
            body=rewritten,
        )

        if args.dry_run:
            continue

        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(final_text, encoding="utf-8")

    if args.verbose:
        print("[sync] done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

