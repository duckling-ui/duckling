# The MIT License (MIT)
#  *
#  * Copyright (c) 2022-present David G. Simmons
#  *
#  * Permission is hereby granted, free of charge, to any person obtaining a copy
#  * of this software and associated documentation files (the "Software"), to deal
#  * in the Software without restriction, including without limitation the rights
#  * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  * copies of the Software, and to permit persons to whom the Software is
#  * furnished to do so, subject to the following conditions:
#  *
#  * The above copyright notice and this permission notice shall be included in all
#  * copies or substantial portions of the Software.
#  *
#  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  * SOFTWARE.

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


