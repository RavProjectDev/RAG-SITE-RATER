import pytest
import json
from rag_endpoint.rav_api.app import create_app

endpoint = "/api/chat/stream"  # ✅ Added leading slash


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_chat_stream(client):
    request_body = {"question": "Why did Moshe sacrifice his family life?"}

    response = client.post(
        endpoint,
        data=json.dumps(request_body),
        content_type="application/json",
    )

    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    # Gather the streamed data
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

        json_str = line[len("data: ") :]
        if json_str == "[DONE]":
            continue

        try:
            payload = json.loads(json_str)
        except json.JSONDecodeError:
            continue

        if isinstance(payload, dict):
            if "metadata" in payload:
                found_metadata = True
            if "data" in payload:
                found_data = True

    assert found_metadata, "Expected a metadata chunk but found none."
    assert found_data, "Expected at least one data chunk but found none."


def test_invalid_request_format(client):
    request_body = {"not_expected_key": "..."}

    response = client.post(
        endpoint,
        data=json.dumps(request_body),
        content_type="application/json",
    )

    assert response.status_code == 400, f"Expected 400 but got {response.status_code}"

    json_data = response.get_json()
    assert json_data is not None, "Expected JSON response but got None"
    assert "error" in json_data, f"Expected 'error' but got {json_data}"


def test_empty_request(client):
    response = client.post(
        endpoint,
        data=json.dumps({}),
        content_type="application/json",
    )

    assert response.status_code == 400, f"Expected 400 but got {response.status_code}"

    json_data = response.get_json()
    assert json_data is not None, "Expected JSON response but got None"
    assert "error" in json_data, f"Expected 'error' but got {json_data}"
