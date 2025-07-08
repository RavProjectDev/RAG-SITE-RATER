from fastapi.testclient import TestClient
from rag.app.main import app
import json
from unittest.mock import patch, MagicMock

client = TestClient(app)


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


@patch("rag.app.api.v1.chat.get_llm_response", return_value="mocked LLM response")
@patch("rag.app.api.v1.chat.verify", return_value=(True, "What is Torah?"))
@patch("rag.app.api.v1.chat.pre_process_user_query", return_value="Torah?")
@patch("rag.app.api.v1.chat.generate_embedding")
def test_chat_handler_success(mock_embed, mock_pre, mock_verify, mock_llm):
    mock_embed.return_value.vector = [0.1, 0.2, 0.3]
    mock_conn = MagicMock()
    mock_conn.retrieve.return_value = []
    app.dependency_overrides = {}
    with client as c:
        c.app.state.mongo_conn = mock_conn
        response = c.post("/api/v1/chat/", json={"question": "What is Torah?"})
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["message"] == "mocked LLM response"


@patch(
    "rag.app.api.v1.chat.stream_llm_response", return_value=iter(["chunk1", "chunk2"])
)
@patch("rag.app.api.v1.chat.verify", return_value=(True, "What is Torah?"))
@patch("rag.app.api.v1.chat.pre_process_user_query", return_value="Torah?")
@patch("rag.app.api.v1.chat.generate_embedding")
def test_chat_stream_success(mock_embed, mock_pre, mock_verify, mock_stream):
    mock_embed.return_value.vector = [0.1, 0.2, 0.3]
    mock_conn = MagicMock()
    mock_conn.retrieve.return_value = []
    app.dependency_overrides = {}
    with client as c:
        c.app.state.mongo_conn = mock_conn
        response = c.post("/api/v1/chat/stream", json={"question": "What is Torah?"})
        assert response.status_code == 200

        payloads = parse_sse(response.content)
        chunk_texts = [p["data"] for p in payloads if "data" in p]

        assert "chunk1" in chunk_texts
        assert "chunk2" in chunk_texts


def test_chat_handler_invalid_event():
    with patch("rag.app.api.v1.chat.verify", return_value=(False, "error")):
        response = client.post("/api/v1/chat/", json={})
        assert response.status_code == 400


def test_chat_handler_internal_error():
    with patch("rag.app.api.v1.chat.verify", side_effect=Exception("fail")):
        response = client.post("/api/v1/chat/", json={"question": "fail"})
        assert response.status_code == 500
