"""
Tests for the Data Operations API Service
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Set test environment variables before importing the app
os.environ.setdefault("ELASTIC_SEARCH_URL", "http://localhost:9200")
os.environ.setdefault("ELASTIC_API_KEY", "test-key")


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self):
        """Test that health endpoint returns healthy status."""
        from api.main import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestSetupEndpoint:
    """Tests for the setup endpoint."""

    def test_setup_requires_elasticsearch_connection(self):
        """Test that setup fails gracefully when ES is unavailable."""
        from api.main import app

        client = TestClient(app)
        # Mock both the direct Elasticsearch import in api.main and the one imported
        # by ingest_skills which is used by the setup endpoint
        with patch("elasticsearch.Elasticsearch") as mock_es_class:
            mock_instance = MagicMock()
            mock_instance.ping.return_value = False
            mock_es_class.return_value = mock_instance

            response = client.post("/api/v1/ops/setup")
            # Should fail because ES connection fails
            assert response.status_code == 500
            assert "connect" in response.json()["detail"].lower()

    def test_setup_with_invalid_api_key(self):
        """Test that setup requires valid API key when configured."""
        from api.main import app

        with patch.dict(os.environ, {"API_SERVICE_KEY": "secret-key"}):
            client = TestClient(app)
            response = client.post(
                "/api/v1/ops/setup", headers={"X-API-Key": "wrong-key"}
            )
            assert response.status_code == 401


class TestTeardownEndpoint:
    """Tests for the teardown endpoint."""

    @patch("api.main.get_es_client")
    def test_teardown_success(self, mock_get_es):
        """Test successful teardown operation."""
        from api.main import app

        mock_es = MagicMock()
        mock_es.indices.exists.return_value = True
        mock_es.indices.delete.return_value = {"acknowledged": True}
        mock_get_es.return_value = mock_es

        client = TestClient(app)
        response = client.post("/api/v1/ops/teardown")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "teardown complete" in data["message"].lower()

    @patch("api.main.get_es_client")
    def test_teardown_handles_missing_indices(self, mock_get_es):
        """Test that teardown handles non-existent indices gracefully."""
        from api.main import app

        mock_es = MagicMock()
        mock_es.indices.exists.return_value = False
        mock_get_es.return_value = mock_es

        client = TestClient(app)
        response = client.post("/api/v1/ops/teardown")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_teardown_with_invalid_api_key(self):
        """Test that teardown requires valid API key when configured."""
        from api.main import app

        with patch.dict(os.environ, {"API_SERVICE_KEY": "secret-key"}):
            client = TestClient(app)
            response = client.post(
                "/api/v1/ops/teardown", headers={"X-API-Key": "wrong-key"}
            )
            assert response.status_code == 401


class TestIngestFolderEndpoint:
    """Tests for the folder ingestion endpoint."""

    def test_ingest_folder_not_found(self):
        """Test that ingesting a non-existent folder returns 400."""
        from api.main import app

        client = TestClient(app)
        response = client.post(
            "/api/v1/ingest/folder",
            json={"folder_name": "nonexistent_folder_xyz123"},
        )

        assert response.status_code == 400
        data = response.json()
        assert "not found" in data["detail"].lower()

    @patch("api.main.get_es_client")
    def test_ingest_folder_success(self, mock_get_es):
        """Test successful folder ingestion."""
        from api.main import app, SAMPLE_SKILLS_DIR

        # Find a real folder to test with
        real_folders = [
            d for d in SAMPLE_SKILLS_DIR.iterdir() if d.is_dir()
        ]

        if not real_folders:
            pytest.skip("No sample skill folders available for testing")

        folder_name = real_folders[0].name

        mock_es = MagicMock()
        mock_es.ping.return_value = True
        mock_es.index.return_value = {"result": "created"}
        mock_get_es.return_value = mock_es

        client = TestClient(app)
        response = client.post(
            "/api/v1/ingest/folder",
            json={"folder_name": folder_name},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["folder"] == folder_name
        assert data["documents_indexed"] == 1
        assert data["errors"] == 0

    def test_ingest_folder_with_invalid_api_key(self):
        """Test that ingest requires valid API key when configured."""
        from api.main import app

        with patch.dict(os.environ, {"API_SERVICE_KEY": "secret-key"}):
            client = TestClient(app)
            response = client.post(
                "/api/v1/ingest/folder",
                json={"folder_name": "test"},
                headers={"X-API-Key": "wrong-key"},
            )
            assert response.status_code == 401


class TestAPIAuthentication:
    """Tests for API authentication."""

    def test_no_auth_required_when_key_not_configured(self):
        """Test that requests work when API_SERVICE_KEY is not set."""
        from api.main import app

        # Ensure API_SERVICE_KEY is not set
        env_backup = os.environ.pop("API_SERVICE_KEY", None)
        try:
            client = TestClient(app)
            response = client.get("/health")
            assert response.status_code == 200
        finally:
            if env_backup:
                os.environ["API_SERVICE_KEY"] = env_backup

    def test_auth_required_when_key_configured(self):
        """Test that requests require auth when API_SERVICE_KEY is set."""
        from api.main import app

        with patch.dict(os.environ, {"API_SERVICE_KEY": "my-secret-key"}):
            client = TestClient(app)
            # Health endpoint doesn't require auth
            response = client.get("/health")
            assert response.status_code == 200

            # But ops endpoints do
            response = client.post("/api/v1/ops/teardown")
            assert response.status_code == 401

    def test_valid_api_key_accepted(self):
        """Test that valid API key is accepted."""
        from api.main import app

        with patch.dict(os.environ, {"API_SERVICE_KEY": "my-secret-key"}):
            with patch("api.main.get_es_client") as mock_get_es:
                mock_es = MagicMock()
                mock_es.indices.exists.return_value = False
                mock_get_es.return_value = mock_es

                client = TestClient(app)
                response = client.post(
                    "/api/v1/ops/teardown",
                    headers={"X-API-Key": "my-secret-key"},
                )
                assert response.status_code == 200


class TestResponseFormat:
    """Tests for API response format compatibility with Elastic Workflows."""

    @patch("api.main.get_es_client")
    def test_response_content_type_is_json(self, mock_get_es):
        """Test that responses have application/json content type."""
        from api.main import app

        mock_es = MagicMock()
        mock_es.indices.exists.return_value = False
        mock_get_es.return_value = mock_es

        client = TestClient(app)
        response = client.post("/api/v1/ops/teardown")

        assert response.headers["content-type"] == "application/json"

    def test_error_response_is_json(self):
        """Test that error responses are also JSON."""
        from api.main import app

        client = TestClient(app)
        response = client.post(
            "/api/v1/ingest/folder",
            json={"folder_name": "nonexistent_folder"},
        )

        assert response.status_code == 400
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert "detail" in data

    @patch("api.main.get_es_client")
    def test_timestamp_format(self, mock_get_es):
        """Test that timestamps are in ISO format."""
        from api.main import app
        import re

        mock_es = MagicMock()
        mock_es.indices.exists.return_value = False
        mock_get_es.return_value = mock_es

        client = TestClient(app)
        response = client.post("/api/v1/ops/teardown")

        data = response.json()
        # Check ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        assert re.match(iso_pattern, data["timestamp"])
