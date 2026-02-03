#!/usr/bin/env python3
"""
The MIT License (MIT)

Copyright (c) 2022-present David G. Simmons

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import urllib.request
    import urllib.error
except ImportError:
    urllib = None


def get_version_from_package_json() -> Optional[str]:
    """Get version from frontend/package.json."""
    root_dir = Path(__file__).parent.parent
    package_json = root_dir / "frontend" / "package.json"

    if not package_json.exists():
        return None

    try:
        with open(package_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            version = data.get("version")
            if version:
                # Remove 'v' prefix if present
                return version.lstrip("v")
    except (json.JSONDecodeError, KeyError, IOError) as e:
        print(f"Warning: Could not read version from package.json: {e}", file=sys.stderr)

    return None


def get_version_from_github() -> Optional[str]:
    """Get latest release version from GitHub API."""
    repo = "davidgs/duckling"
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"

    if urllib is None:
        return None

    try:
        request = urllib.request.Request(api_url)
        # Add User-Agent header (GitHub API requires it)
        request.add_header("User-Agent", "duckling-docs-build")

        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                tag_name = data.get("tag_name", "")
                if tag_name:
                    # Remove 'v' prefix if present
                    return tag_name.lstrip("v")
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError) as e:
        print(f"Warning: Could not fetch version from GitHub: {e}", file=sys.stderr)

    return None


def update_mkdocs_yml(version: str) -> bool:
    """Update version in mkdocs.yml."""
    root_dir = Path(__file__).parent.parent
    mkdocs_yml = root_dir / "mkdocs.yml"

    if not mkdocs_yml.exists():
        print(f"Error: mkdocs.yml not found at {mkdocs_yml}", file=sys.stderr)
        return False

    try:
        with open(mkdocs_yml, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find and update the version line
        updated = False
        in_version_section = False

        for i, line in enumerate(lines):
            if "extra:" in line:
                in_version_section = True
            elif in_version_section and "version:" in line:
                continue
            elif in_version_section and "provider:" in line:
                continue
            elif in_version_section and "default:" in line:
                # Match: default: 0.0.7 or default: 0.0.7  # comment
                pattern = r"(\s*default:\s*)([^\s\n#]+)(.*)$"
                match = re.match(pattern, line)
                if match:
                    lines[i] = match.group(1) + version + match.group(3) + "\n"
                    updated = True
                    break
            elif in_version_section and line.strip() and not line.strip().startswith("#"):
                # We've left the version section
                in_version_section = False

        if updated:
            with open(mkdocs_yml, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True
        else:
            print(f"Warning: Could not find version pattern in mkdocs.yml", file=sys.stderr)
            return False

    except IOError as e:
        print(f"Error: Could not update mkdocs.yml: {e}", file=sys.stderr)
        return False


def create_versions_json(version: str) -> bool:
    """Create versions.json file for mike provider.

    Creates versions.json in both:
    - docs/ directory (for mkdocs serve)
    - site/ directory (for mkdocs build, if it exists)
    """
    root_dir = Path(__file__).parent.parent
    site_dir = root_dir / "site"
    docs_dir = root_dir / "docs"

    # Create versions.json structure that mike expects
    versions_data = [
        {
            "version": version,
            "title": version,
            "aliases": ["latest"]
        }
    ]

    success = False

    # Create in docs directory (for serving)
    docs_versions_json = docs_dir / "versions.json"
    try:
        with open(docs_versions_json, "w", encoding="utf-8") as f:
            json.dump(versions_data, f, indent=2)
        success = True
    except IOError as e:
        print(f"Warning: Could not create versions.json in docs: {e}", file=sys.stderr)

    # Also create in site directory if it exists (for built site)
    if site_dir.exists():
        site_versions_json = site_dir / "versions.json"
        try:
            with open(site_versions_json, "w", encoding="utf-8") as f:
                json.dump(versions_data, f, indent=2)
            success = True
        except IOError as e:
            print(f"Warning: Could not create versions.json in site: {e}", file=sys.stderr)

    return success


def main():
    """Main entry point."""
    # Try package.json first
    version = get_version_from_package_json()

    # Fall back to GitHub if package.json doesn't have version
    if not version:
        version = get_version_from_github()

    # If still no version, use default
    if not version:
        print("Warning: Could not determine version, using default '0.0.7'", file=sys.stderr)
        version = "0.0.7"

    # Update mkdocs.yml
    mkdocs_updated = update_mkdocs_yml(version)

    # Create versions.json for mike provider
    versions_json_created = create_versions_json(version)

    if mkdocs_updated:
        print(f"Updated mkdocs.yml with version: {version}")
    if versions_json_created:
        print(f"Created versions.json with version: {version}")

    # Output version to stdout for use in scripts
    print(version)

    if mkdocs_updated or versions_json_created:
        return 0
    else:
        print(f"Warning: Could not update version files, but version is: {version}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
