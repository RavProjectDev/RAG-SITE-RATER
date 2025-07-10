# tests/test_chat.py

import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from rag.app.main import app

# ---------------------------------------------------------------
# Helper to parse streaming SSE responses into payloads
# ---------------------------------------------------------------


def parse_sse(response_bytes):
    text = response_bytes.decode()
    events = text.strip().split("\n\n")
    payloads = []
    for evt in events:
        if evt.startswith("data: "):
            data = evt[len("data: ") :].strip()
            if not data or data == "[DONE]":
                continue
            payloads.append(json.loads(data))
    return payloads


# ---------------------------------------------------------------
# Fixture: Patch get_settings globally for all chat tests
# ---------------------------------------------------------------


@pytest.fixture(autouse=True)
def patch_get_settings(monkeypatch):
    """
    Ensures all tests use a fake settings object instead of real environment values.
    """

    from rag.app.core import config
    from rag.app.core.config import Environment, EmbeddingConfiguration, LLMModel

    fake_settings = MagicMock()
    fake_settings.environment = Environment.TEST
    fake_settings.openai_api_key = "sk-test"
    fake_settings.sbert_api_url = "http://localhost"
    fake_settings.mongodb_uri = "mongodb://localhost:27017"
    fake_settings.mongodb_db_name = "testdb"
    fake_settings.mongodb_vector_collection = "test_vectors"
    fake_settings.collection_index = "test_index"
    fake_settings.gemini_api_key = "gemini_test_key"
    fake_settings.google_cloud_project_id = "my-project"
    fake_settings.vector_path = "vector"
    fake_settings.vertex_region = "us-central1"
    fake_settings.chunk_size = 100
    fake_settings.external_api_timeout = 30
    fake_settings.metrics_collection = "metrics"
    fake_settings.embedding_configuration = EmbeddingConfiguration.MOCK
    fake_settings.llm_configuration = LLMModel.MOCK

    monkeypatch.setattr(config, "get_settings", lambda: fake_settings)


# ---------------------------------------------------------------
# Test Class for Chat Endpoints
# ---------------------------------------------------------------


class TestChatRoutes:
    @patch("rag.app.api.v1.chat.get_llm_response", return_value="mocked LLM response")
    @patch("rag.app.api.v1.chat.verify", return_value=(True, "What is Torah?"))
    @patch("rag.app.api.v1.chat.pre_process_user_query", return_value="Torah?")
    @patch("rag.app.api.v1.chat.generate_embedding")
    def test_handler_success(self, mock_embed, mock_pre, mock_verify, mock_llm):
        mock_embed.return_value.vector = [0.1, 0.2, 0.3]

        mock_conn = MagicMock()
        mock_conn.retrieve.return_value = []

        app.dependency_overrides = {}
        with TestClient(app) as client:
            client.app.state.mongo_conn = mock_conn
            client.app.state.metrics_connection = MagicMock()

            payload = {"question": "What is Torah?"}
            response = client.post("/api/v1/chat/", json=payload)

            assert response.status_code == 200
            body = response.json()
            assert "message" in body
            assert body["message"] == "mocked LLM response"
            assert isinstance(body["metadata"], list)

    @patch(
        "rag.app.api.v1.chat.stream_llm_response",
        return_value=iter(["chunk1", "chunk2"]),
    )
    @patch("rag.app.api.v1.chat.verify", return_value=(True, "What is Torah?"))
    @patch("rag.app.api.v1.chat.pre_process_user_query", return_value="Torah?")
    @patch("rag.app.api.v1.chat.generate_embedding")
    def test_stream_success(self, mock_embed, mock_pre, mock_verify, mock_stream):
        mock_embed.return_value.vector = [0.1, 0.2, 0.3]

        mock_conn = MagicMock()
        mock_conn.retrieve.return_value = []

        app.dependency_overrides = {}
        with TestClient(app) as client:
            client.app.state.mongo_conn = mock_conn
            client.app.state.metrics_connection = MagicMock()

            payload = {"question": "What is Torah?"}
            response = client.post("/api/v1/chat/stream", json=payload)

            assert response.status_code == 200
            payloads = parse_sse(response.content)
            chunk_texts = [p["data"] for p in payloads if "data" in p]

            assert "chunk1" in chunk_texts
            assert "chunk2" in chunk_texts

    def test_handler_invalid_event(self):
        with patch("rag.app.api.v1.chat.verify", return_value=(False, "error")):
            response = TestClient(app).post("/api/v1/chat/", json={})
            assert response.status_code == 400

    def test_handler_internal_error(self):
        with patch("rag.app.api.v1.chat.verify", side_effect=Exception("fail")):
            response = TestClient(app).post("/api/v1/chat/", json={"question": "fail"})
            assert response.status_code == 500
