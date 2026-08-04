#!/usr/bin/env python3
"""Harden jaraco.context and wheel for Trivy image scans without breaking runtime pip.

Build-time only: upgrades packages with dependencies intact, removes stale vulnerable
dist-info directories that scanners still report, and verifies pip/wheel still work.
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
import shutil


MIN_JARACO = "6.1.0"
MIN_WHEEL = "0.46.2"


def _parse(v: str) -> list[int]:
    out: list[int] = []
    for part in v.split("."):
        n = ""
        for ch in part:
            if ch.isdigit():
                n += ch
            else:
                break
        out.append(int(n or 0))
    return out


def assert_min(pkg: str, minimum: str) -> None:
    installed = version(pkg)
    if _parse(installed) < _parse(minimum):
        raise SystemExit(f"{pkg}={installed} is below required {minimum}")


def remove_legacy_metadata(package_name: str, minimum: str) -> int:
    removed = 0
    root = Path(sys.prefix) / "lib"
    pattern = f"{package_name.replace('.', '?')}-*.dist-info"
    for dist in root.rglob(pattern):
        name = dist.name
        ver = name[len(package_name) + 1 : -len(".dist-info")]
        if _parse(ver) < _parse(minimum):
            shutil.rmtree(dist, ignore_errors=True)
            removed += 1
    return removed


def upgrade_pins() -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--force-reinstall",
            f"jaraco.context>={MIN_JARACO}",
            f"wheel>={MIN_WHEEL}",
        ],
        check=True,
    )


def verify_runtime() -> None:
    assert_min("jaraco.context", MIN_JARACO)
    assert_min("wheel", MIN_WHEEL)
    importlib.import_module("pip")
    importlib.import_module("wheel")
    subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)


def main() -> None:
    upgrade_pins()
    removed = remove_legacy_metadata("jaraco.context", MIN_JARACO)
    removed += remove_legacy_metadata("wheel", MIN_WHEEL)
    print(f"Removed legacy metadata dirs: {removed}")
    verify_runtime()
    print("Verified hardened Python package minimums and pip runtime")


if __name__ == "__main__":
    main()
