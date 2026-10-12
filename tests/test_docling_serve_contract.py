"""Contract tests for docling-serve /v1 API mounted in Duckling ASGI app."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "backend"))

pytest.importorskip("docling_serve")

from asgi import DOCLING_SERVE_ENABLED, app  # noqa: E402


@pytest.fixture
def client():
    from starlette.testclient import TestClient

    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.skipif(not DOCLING_SERVE_ENABLED, reason="docling-serve not mounted")
def test_openapi_schema_available(client):
    response = client.get("/openapi-3.0.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})
    assert "/v1/convert/file" in paths
    assert "/v1/convert/source" in paths
    assert "/v1/status/poll/{task_id}" in paths


@pytest.mark.skipif(not DOCLING_SERVE_ENABLED, reason="docling-serve not mounted")
def test_health_and_version(client):
    assert client.get("/health").status_code == 200
    version = client.get("/version")
    assert version.status_code == 200
    assert "docling" in version.text.lower() or "version" in version.json()


@pytest.mark.skipif(not DOCLING_SERVE_ENABLED, reason="docling-serve not mounted")
def test_duckling_api_still_mounted(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"


@pytest.mark.skipif(not DOCLING_SERVE_ENABLED, reason="docling-serve not mounted")
def test_openapi_paths_golden_subset():
    """Critical /v1 paths must remain stable for API equality."""
    golden_path = Path(__file__).parent / "fixtures" / "docling_serve_paths.json"
    expected = {
        "/v1/convert/source",
        "/v1/convert/file",
        "/v1/convert/source/async",
        "/v1/convert/file/async",
        "/v1/status/poll/{task_id}",
        "/v1/result/{task_id}",
        "/v1/chunk/hybrid/source",
        "/v1/chunk/hierarchical/file",
    }
    if golden_path.exists():
        expected = set(json.loads(golden_path.read_text(encoding="utf-8")))
    from starlette.testclient import TestClient

    client = TestClient(app, raise_server_exceptions=False)
    schema = client.get("/openapi-3.0.json").json()
    actual = {p for p in schema.get("paths", {}) if p.startswith("/v1/")}
    missing = expected - actual
    assert not missing, f"Missing expected /v1 paths: {missing}"
