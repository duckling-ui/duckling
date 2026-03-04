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

import ipaddress
import re
import socket
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from werkzeug.utils import safe_join
from werkzeug.exceptions import NotFound, BadRequest

# SSRF: Blocked IP ranges (loopback, private, link-local, metadata)
_SSRF_BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),   # Loopback
    ipaddress.ip_network("0.0.0.0/8"),    # Current network (also 0.0.0.0)
    ipaddress.ip_network("10.0.0.0/8"),   # Private
    ipaddress.ip_network("172.16.0.0/12"), # Private
    ipaddress.ip_network("192.168.0.0/16"), # Private
    ipaddress.ip_network("169.254.0.0/16"), # Link-local / cloud metadata
    ipaddress.ip_network("::1/128"),       # IPv6 loopback
    ipaddress.ip_network("fe80::/10"),     # IPv6 link-local
    ipaddress.ip_network("fc00::/7"),      # IPv6 unique local
]

# Hostnames that resolve to internal resources
_SSRF_BLOCKED_HOSTNAMES = frozenset({"localhost", "localhost.localdomain"})


def _parse_host_to_ips(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    """Parse host (IP or hostname) to list of IP addresses. Raises on failure."""
    if not host:
        raise BadRequest("Invalid URL: missing host")

    # Try parsing as IP address (handles IPv4, IPv6, decimal, hex, octal forms)
    try:
        # IPv4 decimal form (e.g. 2130706433 -> 127.0.0.1)
        if host.isdigit():
            return [ipaddress.ip_address(int(host))]
        # IPv4 hex form (e.g. 0x7f000001)
        if host.lower().startswith("0x") and len(host) > 2:
            return [ipaddress.ip_address(int(host, 16))]
        # IPv4 octal form (e.g. 0177.0.0.1) - each octet can be octal
        # Standard parsing
        return [ipaddress.ip_address(host)]
    except ValueError:
        pass

    # Resolve hostname to IP(s)
    try:
        # getaddrinfo returns all resolved addresses
        infos = socket.getaddrinfo(host, None)
        ips = []
        for info in infos:
            addr = info[4][0]
            ips.append(ipaddress.ip_address(addr))
        return ips
    except socket.gaierror:
        raise BadRequest("Invalid URL: cannot resolve host")


def validate_url_safe_for_request(url: str) -> str:
    """
    Validate that a URL is safe for outbound HTTP requests (SSRF prevention).

    Blocks loopback, private, link-local, and metadata IP ranges.
    Blocks dangerous schemes (only http/https allowed).
    Must be called before any requests.get/post with user-controlled URLs.

    Returns:
        The validated URL (for use in requests - satisfies CodeQL data flow)

    Raises:
        BadRequest: If the URL targets internal or blocked resources
    """
    try:
        parsed = urlparse(url)
    except Exception:
        raise BadRequest("Invalid URL format")

    if parsed.scheme not in ("http", "https"):
        raise BadRequest("Only HTTP and HTTPS URLs are supported")

    host = (parsed.hostname or "").strip().lower()
    if not host:
        raise BadRequest("Invalid URL: missing host")

    # Block known-bad hostnames
    if host in _SSRF_BLOCKED_HOSTNAMES or host.endswith(".localhost"):
        raise BadRequest("URL not allowed")

    # Resolve and check all IPs
    for ip in _parse_host_to_ips(host):
        for network in _SSRF_BLOCKED_NETWORKS:
            if ip in network:
                raise BadRequest("URL not allowed")

    # Return reconstructed URL (breaks taint flow for CodeQL - new string from validated components)
    return parsed.geturl()


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
