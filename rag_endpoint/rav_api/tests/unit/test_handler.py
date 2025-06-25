import pytest
import json
from flask import Flask
from rav_api.app import chat_bp  # Adjust if blueprint is in another path

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(chat_bp, url_prefix="/chat")
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_valid_request(client):
    request_body = {
        "question": "Why did Moshe sacrifice his family life?"
    }

    response = client.post("/chat/", data=json.dumps(request_body), content_type="application/json")
    assert response.status_code == 200
    assert "message" in response.get_json()

def test_invalid_request_format(client):
    # Missing user_question or malformed input
    request_body = {"not_expected_key": "..."}

    response = client.post("/chat/", data=json.dumps(request_body), content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_empty_request(client):
    response = client.post("/chat/", data=json.dumps({}), content_type="application/json")
    assert response.status_code == 400
    assert "error" in response.get_json()
