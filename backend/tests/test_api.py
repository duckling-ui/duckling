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

"""Tests for API endpoints."""

import io
import json
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns OK."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["service"] == "duckling-backend"


class TestFormatsEndpoint:
    """Tests for formats endpoint."""

    def test_get_formats(self, client):
        """Test getting supported formats."""
        response = client.get("/api/formats")
        assert response.status_code == 200
        data = json.loads(response.data)

        assert "input_formats" in data
        assert "output_formats" in data
        assert len(data["input_formats"]) > 0
        assert len(data["output_formats"]) > 0

    def test_input_formats_structure(self, client):
        """Test input formats have correct structure."""
        response = client.get("/api/formats")
        data = json.loads(response.data)

        for fmt in data["input_formats"]:
            assert "id" in fmt
            assert "name" in fmt
            assert "extensions" in fmt

    def test_output_formats_structure(self, client):
        """Test output formats have correct structure."""
        response = client.get("/api/formats")
        data = json.loads(response.data)

        for fmt in data["output_formats"]:
            assert "id" in fmt
            assert "name" in fmt
            assert "extension" in fmt


class TestConvertEndpoint:
    """Tests for conversion endpoints."""

    def test_convert_no_file(self, client):
        """Test conversion without file returns error."""
        response = client.post("/api/convert")
        assert response.status_code == 400

    def test_convert_empty_filename(self, client):
        """Test conversion with empty filename returns error."""
        data = {"file": (io.BytesIO(b"test"), "")}
        response = client.post(
            "/api/convert",
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 400

    def test_convert_invalid_extension(self, client):
        """Test conversion with invalid file type."""
        data = {"file": (io.BytesIO(b"test"), "file.xyz")}
        response = client.post(
            "/api/convert",
            data=data,
            content_type="multipart/form-data"
        )
        assert response.status_code == 400

    def test_convert_valid_file(self, client, sample_markdown_content):
        """Test conversion with valid markdown file."""
        data = {"file": (io.BytesIO(sample_markdown_content), "test.md")}
        response = client.post(
            "/api/convert",
            data=data,
            content_type="multipart/form-data"
        )

        # Should return 202 Accepted for async processing
        assert response.status_code == 202
        result = json.loads(response.data)
        assert "job_id" in result
        assert result["status"] == "processing"

    def test_get_status_nonexistent_job(self, client):
        """Test getting status of non-existent job."""
        response = client.get("/api/convert/nonexistent-id/status")
        assert response.status_code == 404


class TestSettingsEndpoint:
    """Tests for settings endpoints."""

    def test_get_settings(self, client):
        """Test getting current settings."""
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = json.loads(response.data)

        assert "settings" in data
        assert "defaults" in data

    def test_update_settings(self, client):
        """Test updating settings."""
        new_settings = {
            "ocr": {"enabled": False}
        }
        response = client.put(
            "/api/settings",
            data=json.dumps(new_settings),
            content_type="application/json"
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["settings"]["ocr"]["enabled"] is False

    def test_reset_settings(self, client):
        """Test resetting settings to defaults."""
        response = client.post("/api/settings/reset")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "settings" in data


class TestDocsEndpoints:
    """Tests for documentation endpoints."""

    @pytest.mark.parametrize("lang", ["en", "es", "fr", "de"])
    def test_list_docs_accepts_language(self, client, lang):
        """Test /api/docs accepts supported languages and returns metadata."""
        response = client.get(f"/api/docs?lang={lang}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["language"] in ["en", "es", "fr", "de"]
        assert "available_languages" in data
        assert set(["en", "es", "fr", "de"]).issubset(set(data["available_languages"]))

    def test_list_docs_invalid_language_falls_back_to_en(self, client):
        """Test /api/docs falls back to en for unsupported languages."""
        response = client.get("/api/docs?lang=xx")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["language"] == "en"

    def test_list_docs_en_does_not_include_locale_roots(self, client):
        """Default locale listing should not treat /site/<locale>/ as docs pages."""
        response = client.get("/api/docs?lang=en")
        assert response.status_code == 200
        data = json.loads(response.data)
        docs = data.get("docs", [])

        # Ensure we don't accidentally include locale root pages like "es/index.html"
        paths = {d.get("path", "") for d in docs}
        assert "es" not in paths
        assert "fr" not in paths
        assert "de" not in paths

    def test_list_docs_de_uses_localized_titles_when_available(self, client):
        """German docs listing should use localized page titles from built HTML when present."""
        response = client.get("/api/docs?lang=de")
        assert response.status_code == 200
        data = json.loads(response.data)
        docs = data.get("docs", [])

        # "deployment/security" is translated to "Sicherheit" in the German docs we ship.
        security = next((d for d in docs if d.get("path") == "deployment/security"), None)
        assert security is not None
        assert "Sicherheit" in (security.get("name") or "")

    def test_get_ocr_settings(self, client):
        """Test getting OCR settings."""
        response = client.get("/api/settings/ocr")
        assert response.status_code == 200
        data = json.loads(response.data)

        assert "ocr" in data
        assert "available_languages" in data

    def test_update_ocr_settings(self, client):
        """Test updating OCR settings."""
        response = client.put(
            "/api/settings/ocr",
            data=json.dumps({"enabled": True, "language": "de"}),
            content_type="application/json"
        )
        assert response.status_code == 200

    def test_get_table_settings(self, client):
        """Test getting table settings."""
        response = client.get("/api/settings/tables")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "tables" in data

    def test_get_output_settings(self, client):
        """Test getting output settings."""
        response = client.get("/api/settings/output")
        assert response.status_code == 200
        data = json.loads(response.data)

        assert "output" in data
        assert "available_formats" in data


class TestHistoryEndpoint:
    """Tests for history endpoints."""

    def test_get_history(self, client):
        """Test getting history."""
        response = client.get("/api/history")
        assert response.status_code == 200
        data = json.loads(response.data)

        assert "entries" in data
        assert "count" in data
        assert "limit" in data
        assert "offset" in data

    def test_get_recent_history(self, client):
        """Test getting recent history."""
        response = client.get("/api/history/recent")
        assert response.status_code == 200
        data = json.loads(response.data)

        assert "entries" in data
        assert "count" in data

    def test_get_history_stats(self, client):
        """Test getting history statistics."""
        response = client.get("/api/history/stats")
        assert response.status_code == 200
        data = json.loads(response.data)

        assert "conversions" in data
        assert "storage" in data

    def test_search_history_empty(self, client):
        """Test searching history with empty query."""
        response = client.get("/api/history/search?q=")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["count"] == 0

    def test_search_history(self, client):
        """Test searching history."""
        response = client.get("/api/history/search?q=test")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "entries" in data
        assert "query" in data

    def test_get_nonexistent_history_entry(self, client):
        """Test getting non-existent history entry."""
        response = client.get("/api/history/nonexistent-id")
        assert response.status_code == 404

    def test_delete_nonexistent_history_entry(self, client):
        """Test deleting non-existent history entry."""
        response = client.delete("/api/history/nonexistent-id")
        assert response.status_code == 404

    def test_export_history(self, client):
        """Test exporting history."""
        response = client.get("/api/history/export")
        assert response.status_code == 200
        data = json.loads(response.data)

        assert "exported_at" in data
        assert "entries" in data
        assert "statistics" in data


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.put(
            "/api/settings",
            data="invalid json",
            content_type="application/json"
        )
        assert response.status_code in [400, 500]

