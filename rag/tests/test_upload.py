# tests/test_upload.py

import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from rag.app.main import app
from rag.app.core import config
from rag.app.core.config import Environment
from rag.app.schemas.data import Chunk, VectorEmbedding

client = TestClient(app)

# ---------------------------------------------------------------
# Fixture: force test environment
# ---------------------------------------------------------------


@pytest.fixture(autouse=True)
def force_test_env():
    """
    Ensures we run in test mode for every test
    (skips metrics logging, avoids prod config).
    """
    config.get_settings().environment = Environment.TEST


# ---------------------------------------------------------------
# Helper to generate dummy .srt file content
# ---------------------------------------------------------------


def make_srt_file(
    name="test.srt", content="1\n00:00:00,000 --> 00:00:02,000\nHello world."
):
    return (name, io.BytesIO(content.encode("utf-8")), "text/plain")


# ---------------------------------------------------------------
# Test Class for Upload Endpoint
# ---------------------------------------------------------------


class TestUploadRoutes:
    @patch("rag.app.api.v1.upload.embedding_helper")
    @patch("rag.app.api.v1.upload.preprocess_raw_transcripts")
    def test_upload_single_file(self, mock_preprocess, mock_embedding_helper):
        # Mock the preprocessing step
        dummy_chunk = Chunk(
            text="Hello world.",
            chunk_size=12,
            time_start="00:00:00,000",
            time_end="00:00:02,000",
            name_space="test.srt",
            id=None,
        )
        mock_preprocess.return_value = [dummy_chunk]

        # Mock the embedding helper
        dummy_embedding = VectorEmbedding(
            vector=[0.1, 0.2, 0.3],
            dimension=3,
            data=dummy_chunk,
        )
        mock_embedding_helper.return_value = [dummy_embedding]

        mock_conn = MagicMock()
        app.dependency_overrides = {}
        with client as c:
            c.app.state.mongo_conn = mock_conn
            c.app.state.metrics_connection = MagicMock()

            file_data = make_srt_file()
            files = [("files", file_data)]

            response = c.post("/api/v1/upload/", files=files)

            assert response.status_code == 200
            body = response.json()
            assert "results" in body
            assert isinstance(body["results"], list)
            assert len(body["results"]) == 1
            assert body["results"][0]["vector"] == [0.1, 0.2, 0.3]

    @patch("rag.app.api.v1.upload.embedding_helper")
    @patch("rag.app.api.v1.upload.preprocess_raw_transcripts")
    def test_upload_multiple_files(self, mock_preprocess, mock_embedding_helper):
        dummy_chunk = Chunk(
            text="Hello world.",
            chunk_size=12,
            time_start="00:00:00,000",
            time_end="00:00:02,000",
            name_space="test.srt",
            id=None,
        )
        mock_preprocess.return_value = [dummy_chunk]

        dummy_embedding = VectorEmbedding(
            vector=[0.1, 0.2, 0.3],
            dimension=3,
            data=dummy_chunk,
        )
        mock_embedding_helper.return_value = [dummy_embedding]

        mock_conn = MagicMock()
        app.dependency_overrides = {}
        with client as c:
            c.app.state.mongo_conn = mock_conn
            c.app.state.metrics_connection = MagicMock()

            file1 = make_srt_file(name="test1.srt")
            file2 = make_srt_file(name="test2.srt")

            files = [
                ("files", file1),
                ("files", file2),
            ]

            response = c.post("/api/v1/upload/", files=files)

            assert response.status_code == 200
            body = response.json()
            assert "results" in body
            assert isinstance(body["results"], list)
            assert len(body["results"]) == 1  # preprocess returns 1 chunk for all

    def test_upload_invalid_file_extension(self):
        file_data = ("test.txt", io.BytesIO(b"Invalid text file."), "text/plain")
        files = [("files", file_data)]

        response = client.post("/api/v1/upload/", files=files)

        assert response.status_code == 400
        body = response.json()
        assert "detail" in body
        assert "must be an .srt file" in body["detail"]

    @patch(
        "rag.app.api.v1.upload.preprocess_raw_transcripts",
        side_effect=Exception("fail"),
    )
    def test_upload_internal_error(self, mock_preprocess):
        file_data = make_srt_file()
        files = [("files", file_data)]

        response = client.post("/api/v1/upload/", files=files)

        assert response.status_code == 500
        body = response.json()
        assert "detail" in body
        assert "fail" in body["detail"]
