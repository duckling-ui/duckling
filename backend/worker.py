"""Worker entry points for async engine modes."""

from __future__ import annotations

import argparse
import os
import sys
import time


def _run_rq_worker() -> int:
    """Start docling-jobkit / docling-serve RQ worker when dependencies are installed."""
    try:
        from docling_serve.rq_worker_instrumented import main as rq_main  # type: ignore

        return int(rq_main() or 0)
    except ImportError:
        try:
            from rq import Worker
            import redis

            redis_url = os.getenv(
                "DUCKLING_RQ_REDIS_URL",
                os.getenv("DOCLING_SERVE_RQ_REDIS_URL", "redis://redis:6379/0"),
            )
            queue_name = os.getenv(
                "DUCKLING_RQ_QUEUE_NAME",
                os.getenv("DOCLING_SERVE_RQ_QUEUE_NAME", "convert"),
            )
            conn = redis.from_url(redis_url)
            worker = Worker([queue_name], connection=conn)
            print(f"[worker] RQ worker listening on {queue_name} ({redis_url})")
            worker.work(with_scheduler=True)
            return 0
        except Exception as exc:
            print(f"[worker] RQ worker unavailable: {exc}", file=sys.stderr)
            return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Duckling worker process")
    parser.add_argument(
        "--engine",
        choices=["local", "rq", "ray"],
        default=os.getenv("DUCKLING_ENGINE_KIND", "local"),
    )
    args = parser.parse_args()

    if args.engine == "rq":
        return _run_rq_worker()

    if args.engine == "ray":
        print("[worker] Ray mode: connect workers to docling-serve Ray orchestrator (see docs/deployment/scaling.md)")
        while True:
            time.sleep(3600)

    print(f"[worker] engine={args.engine} initialized (local mode uses API process)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
