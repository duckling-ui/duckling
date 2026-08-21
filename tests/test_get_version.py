"""Tests for scripts/get_version.py mkdocs version injection."""

import importlib.util
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def _load_get_version():
    path = PROJECT_ROOT / "scripts" / "get_version.py"
    spec = importlib.util.spec_from_file_location("get_version", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["get_version"] = module
    spec.loader.exec_module(module)
    return module


SAMPLE_MKDOCS = """\
plugins:
  - i18n:
      fallback_to_default: true
      languages:
        - locale: en
          default: true
extra:
  version:
    provider: mike
    default: 0.0.14
"""


def test_update_mkdocs_yml_preserves_i18n_fallback_to_default(tmp_path):
    gv = _load_get_version()
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(SAMPLE_MKDOCS, encoding="utf-8")

    assert gv.update_mkdocs_yml("0.0.14-doclang-beta.3", mkdocs)

    result = mkdocs.read_text(encoding="utf-8")
    assert "fallback_to_default: true" in result
    assert "          default: true" in result
    assert "    default: 0.0.14-doclang-beta.3" in result
    assert "fallback_to_default: 0.0.14-doclang-beta.3" not in result


def test_docs_workflows_use_get_version_not_broad_sed():
    publish = (PROJECT_ROOT / ".github/workflows/publish-docker.yml").read_text(encoding="utf-8")
    deploy = (PROJECT_ROOT / ".github/workflows/deploy-docs-version.yml").read_text(encoding="utf-8")
    assert "python scripts/get_version.py" in publish
    assert "python scripts/get_version.py" in deploy
    assert 'sed -i "s/\\(default:' not in publish
    assert 'sed -i "s/\\(default:' not in deploy


def test_release_version_sources_agree_on_0_1_0():
    """Stable 0.1.0 bump keeps package.json, UI constant, and mike default aligned."""
    import json
    import re

    package = json.loads((PROJECT_ROOT / "frontend/package.json").read_text(encoding="utf-8"))
    assert package["version"] == "0.1.0"

    app = (PROJECT_ROOT / "frontend/src/App.tsx").read_text(encoding="utf-8")
    assert 'const APP_VERSION = "0.1.0"' in app

    mkdocs = (PROJECT_ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert re.search(r"(?m)^\s+default:\s+0\.1\.0\s*$", mkdocs)

    get_version = (PROJECT_ROOT / "scripts/get_version.py").read_text(encoding="utf-8")
    assert 'version = "0.1.0"' in get_version

    changelog = (PROJECT_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "**Latest release:** [0.1.0]" in changelog
    assert "## [0.1.0] - 2026-08-21" in changelog
    assert "docling-serve parity for conversion" in changelog
