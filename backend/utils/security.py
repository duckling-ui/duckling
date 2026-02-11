# The MIT License (MIT)
#
# Copyright (c) 2022-present David G. Simmons
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Security utilities for path validation and sanitization."""

import re
from pathlib import Path
from typing import Optional

from werkzeug.utils import safe_join
from werkzeug.exceptions import NotFound


def validate_job_id(job_id: str) -> str:
    """
    Validate job_id so it cannot be used for path traversal.

    Only allows a conservative set of characters (alphanumerics, dash,
    underscore) and rejects anything else, including dots and path separators.

    Args:
        job_id: The job identifier from the request

    Returns:
        The validated job_id

    Raises:
        NotFound: If job_id is invalid
    """
    if not isinstance(job_id, str):
        raise NotFound("Invalid job identifier")

    if not re.fullmatch(r"[A-Za-z0-9_-]+", job_id):
        raise NotFound("Resource not found")

    return job_id


def get_validated_output_dir(job_id: str, output_folder: Path) -> Path:
    """
    Get safe, validated output directory path for job_id.

    Uses safe_join and resolves path to ensure it stays within output_folder,
    preventing path traversal and symlink escape attacks.

    Args:
        job_id: Must be pre-validated with validate_job_id()
        output_folder: The base output directory (e.g. OUTPUT_FOLDER)

    Returns:
        Path to the validated output directory

    Raises:
        NotFound: If path is outside output_folder or invalid
    """
    joined = safe_join(str(output_folder), job_id)
    if not joined:
        raise NotFound("Resource not found")

    candidate_dir = Path(joined)
    output_folder_resolved = output_folder.resolve()
    try:
        candidate_dir.resolve().relative_to(output_folder_resolved)
    except ValueError:
        raise NotFound("Resource not found")

    return candidate_dir
