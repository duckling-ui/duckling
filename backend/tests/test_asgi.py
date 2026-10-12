"""ASGI composite app structure tests."""

import os
from pathlib import Path


def test_asgi_module_exists():
    assert Path(__file__).parent.parent / "asgi.py"


def test_asgi_exports_app():
    import asgi

    assert hasattr(asgi, "app")
    assert hasattr(asgi, "DOCLING_SERVE_ENABLED")


def test_flask_api_prefix_when_asgi_mounted(monkeypatch):
    monkeypatch.setenv("DUCKLING_ASGI_MOUNTED", "1")
    from duckling import api_route_path, public_api_path, flask_api_prefix

    assert flask_api_prefix() == ""
    assert api_route_path("/convert") == "/convert"
    assert public_api_path("/convert") == "/api/convert"


def test_flask_api_prefix_standalone(monkeypatch):
    monkeypatch.delenv("DUCKLING_ASGI_MOUNTED", raising=False)
    from duckling import api_route_path, flask_api_prefix

    assert flask_api_prefix() == "/api"
    assert api_route_path("/convert") == "/api/convert"
