"""Worker entry points for async engine modes."""

from __future__ import annotations

import argparse
import os


def main() -> int:
    parser = argparse.ArgumentParser(description="Duckling worker process")
    parser.add_argument("--engine", choices=["local", "rq", "ray"], default=os.getenv("DUCKLING_ENGINE_KIND", "local"))
    args = parser.parse_args()
    # Current implementation keeps conversion work in the main API process.
    # This command exists as a stable contract for upcoming RQ/Ray execution modes.
    print(f"[worker] engine={args.engine} initialized (standby mode)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

