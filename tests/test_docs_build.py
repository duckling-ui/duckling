from pathlib import Path


def test_backend_build_docs_prefers_repo_venv_mkdocs():
    """
    Static regression test: ensure backend docs rebuild prefers the repo-local ./venv
    (so required MkDocs plugins like mkdocs-static-i18n are available).
    """
    p = Path(__file__).resolve().parents[1] / "backend" / "duckling.py"
    text = p.read_text(encoding="utf-8")

    assert 'PROJECT_ROOT / "venv" / "bin" / "python"' in text
    assert 'PROJECT_ROOT / "venv" / "bin" / "mkdocs"' in text
    # Ensure we try venv-based mkdocs before PATH mkdocs
    assert "path_mkdocs = shutil.which(\"mkdocs\")" in text
