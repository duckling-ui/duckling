"""Tests for Docker image Python package hardening script."""

from pathlib import Path


def test_harden_script_upgrades_with_deps_and_verifies_pip_runtime():
    script = Path(__file__).resolve().parents[1] / "scripts" / "harden_python_packages.py"
    text = script.read_text(encoding="utf-8")
    assert "--no-deps" not in text
    assert "remove_legacy_ensurepip_wheels" not in text
    assert 'f"jaraco.context>={MIN_JARACO}"' in text
    assert 'f"wheel>={MIN_WHEEL}"' in text
    assert 'importlib.import_module("pip")' in text
    assert 'importlib.import_module("wheel")' in text
    assert '[sys.executable, "-m", "pip", "--version"]' in text
