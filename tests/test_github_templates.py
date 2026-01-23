from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent


def test_github_templates_exist():
    """Ensure GitHub issue + PR templates exist (repo community health)."""
    required_files = [
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/ISSUE_TEMPLATE/question.yml",
        ".github/pull_request_template.md",
    ]

    missing = [p for p in required_files if not (PROJECT_ROOT / p).exists()]
    assert not missing, f"Missing GitHub template files: {missing}"


def test_issue_template_config_has_expected_fields():
    config_path = PROJECT_ROOT / ".github/ISSUE_TEMPLATE/config.yml"
    text = config_path.read_text(encoding="utf-8")

    assert "blank_issues_enabled" in text
    assert "contact_links" in text


def test_bug_template_mentions_security_policy():
    bug_path = PROJECT_ROOT / ".github/ISSUE_TEMPLATE/bug_report.yml"
    text = bug_path.read_text(encoding="utf-8")

    # Keep it simple: validate the template nudges users away from public security disclosure
    assert "SECURITY.md" in text


