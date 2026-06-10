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
    default: 0.0.13
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
