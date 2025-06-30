import pytest
import json
from flask import Flask
from rag_endpoint.rav_api.rav_endpoint.main import chat_bp

endpoint = "/chat/stream"
@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(chat_bp, url_prefix="/chat")
    return app


@pytest.fixture
def client(app):
    return app.test_client()
def test_chat_stream(client):
    request_body = {
        "question": "Why did Moshe sacrifice his family life?"
    }
    response = client.post(
        "/chat/stream",
        data=json.dumps(request_body),
        content_type="application/json"
    )
    assert response.status_code == 200

    response_data = b"".join(response.response).decode("utf-8")
    lines = response_data.strip().split("\n")

    found_metadata = False
    found_data = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if not line.startswith("data: "):
            continue

        json_str = line[len("data: "):]
        if json_str == "[DONE]":
            continue

        try:
            payload = json.loads(json_str)
        except json.JSONDecodeError:
            continue

        if isinstance(payload, dict) and "metadata" in payload:
            found_metadata = True
        if isinstance(payload, dict) and "data" in payload:
            found_data = True

    assert found_metadata, "Expected a metadata chunk but found none."
    assert found_data, "Expected at least one data chunk but found none."

def test_invalid_request_format(client):
    request_body = {"not_expected_key": "..."}

    response = client.post(endpoint, data=json.dumps(request_body), content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_empty_request(client):
    response = client.post(endpoint, data=json.dumps({}), content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.get_json()
