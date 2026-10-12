"""Delegate Duckling /api/convert jobs to docling-serve /v1 when enabled."""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from config import OUTPUT_FOLDER, SERVER_CONFIG
from services.converter import ConversionJob, ConversionStatus, converter_service
from services.settings_mapper import duckling_settings_to_options_dict

logger = logging.getLogger(__name__)

_POLL_INTERVAL = float(os.getenv("DUCKLING_DOCLING_SERVE_POLL_INTERVAL", "1.0"))


def use_docling_serve_engine() -> bool:
    return bool(SERVER_CONFIG.get("use_docling_serve_engine", False))


def _get_test_client():
    """In-process ASGI client (avoids HTTP loopback deadlocks)."""
    try:
        from starlette.testclient import TestClient
        from asgi import app as asgi_app, DOCLING_SERVE_ENABLED

        if not DOCLING_SERVE_ENABLED:
            return None
        return TestClient(asgi_app, raise_server_exceptions=False)
    except Exception as exc:
        logger.warning("docling-serve TestClient unavailable: %s", exc)
        return None


def _materialize_markdown(job: ConversionJob, document: Dict[str, Any]) -> None:
    """Write markdown export from docling-serve JSON document to Duckling output layout."""
    job_dir = OUTPUT_FOLDER / job.id
    job_dir.mkdir(parents=True, exist_ok=True)
    md_path = job_dir / f"{Path(job.filename).stem}.md"
    md_content = ""
    if isinstance(document, dict):
        md_content = document.get("md_content") or document.get("markdown") or ""
        if not md_content and "texts" in document:
            md_content = "\n\n".join(
                t.get("text", "") for t in document.get("texts", []) if isinstance(t, dict)
            )
    md_path.write_text(md_content or "", encoding="utf-8")
    job.output_paths["markdown"] = md_path
    job.result = {
        "markdown_preview": (md_content or "")[:2000],
        "page_count": document.get("num_pages") if isinstance(document, dict) else None,
    }


def _poll_and_finalize(
    job: ConversionJob,
    task_id: str,
    on_complete: Optional[Callable[[ConversionJob], None]],
    history_updater: Optional[Callable[..., None]],
) -> None:
    client = _get_test_client()
    if client is None:
        job.status = ConversionStatus.FAILED
        job.error = "docling-serve engine not available"
        if on_complete:
            on_complete(job)
        return

    try:
        while True:
            poll = client.get(f"/v1/status/poll/{task_id}")
            if poll.status_code != 200:
                job.status = ConversionStatus.FAILED
                job.error = f"poll failed: {poll.status_code}"
                break
            data = poll.json()
            status = (data.get("task_status") or data.get("status") or "").lower()
            job.progress = int(data.get("progress", job.progress) or 0)
            job.message = data.get("message") or job.message
            if status in ("pending", "started", "running", "processing"):
                time.sleep(_POLL_INTERVAL)
                continue
            if status in ("success", "completed", "finished"):
                result_resp = client.get(f"/v1/result/{task_id}")
                if result_resp.status_code == 200:
                    payload = result_resp.json()
                    document = payload.get("document") if isinstance(payload, dict) else payload
                    _materialize_markdown(job, document if isinstance(document, dict) else {})
                    job.status = ConversionStatus.COMPLETED
                    job.progress = 100
                    job.confidence = payload.get("confidence") if isinstance(payload, dict) else None
                else:
                    job.status = ConversionStatus.FAILED
                    job.error = f"result fetch failed: {result_resp.status_code}"
                break
            job.status = ConversionStatus.FAILED
            job.error = data.get("error") or f"task {status}"
            break
    except Exception as exc:
        logger.exception("docling-serve poll error for task %s", task_id)
        job.status = ConversionStatus.FAILED
        job.error = str(exc)
    finally:
        if job.status in (ConversionStatus.COMPLETED, ConversionStatus.FAILED):
            job.completed_at = datetime.utcnow()
        if history_updater:
            history_updater(job)
        if on_complete:
            on_complete(job)


def submit_file_conversion(
    job: ConversionJob,
    file_path: str,
    filename: str,
    on_complete: Optional[Callable[[ConversionJob], None]] = None,
    history_updater: Optional[Callable[..., None]] = None,
) -> str:
    """
    Submit a file conversion via docling-serve async API.

    Returns docling-serve task_id (also stored on job as external_task_id).
    """
    client = _get_test_client()
    if client is None:
        raise RuntimeError("docling-serve is not installed or not enabled in asgi.py")

    options = duckling_settings_to_options_dict(job.settings or {})
    with open(file_path, "rb") as handle:
        response = client.post(
            "/v1/convert/file/async",
            files={"files": (filename, handle, "application/octet-stream")},
            data={"options": json.dumps(options)},
        )
    if response.status_code not in (200, 202):
        raise RuntimeError(f"docling-serve submit failed: {response.status_code} {response.text[:500]}")

    payload = response.json()
    task_id = payload.get("task_id") or payload.get("id") or str(uuid.uuid4())
    job.external_task_id = task_id
    job.status = ConversionStatus.PROCESSING
    job.message = "Submitted to docling-serve"
    converter_service._jobs[job.id] = job  # noqa: SLF001 - mirror in-memory job table

    thread = threading.Thread(
        target=_poll_and_finalize,
        args=(job, task_id, on_complete, history_updater),
        daemon=True,
        name=f"docling-serve-poll-{task_id}",
    )
    thread.start()
    return task_id
