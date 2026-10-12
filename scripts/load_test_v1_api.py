#!/usr/bin/env python3
"""Lightweight concurrent /v1 + /api health load probe."""

from __future__ import annotations

import concurrent.futures
import sys
import urllib.request


def _get(url: str) -> int:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.status
    except Exception:
        return 0


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5001"
    urls = [f"{base}/health", f"{base}/api/health", f"{base}/version"]
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    tasks = [urls[i % len(urls)] for i in range(workers * rounds)]
    ok = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for status in pool.map(_get, tasks):
            if status == 200:
                ok += 1
    print(f"ok={ok}/{len(tasks)} base={base}")
    return 0 if ok == len(tasks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
