import pytest
import json
from rag_endpoint.rav_api.app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_valid_request(client):
    request_body = {"question": "Why did Moshe sacrifice his family life?"}

    response = client.post(
        "/api/chat/",
        data=json.dumps(request_body),
        content_type="application/json",
    )

    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    json_data = response.get_json()
    assert json_data is not None, "Expected JSON response but got None"

    assert "message" in json_data, f"Expected 'message' but got {json_data}"


def test_invalid_request_format(client):
    request_body = {"not_expected_key": "..."}

    response = client.post(
        "/api/chat/",
        data=json.dumps(request_body),
        content_type="application/json",
    )

    json_data = response.get_json()
    assert json_data is not None, "Expected JSON response but got None"

    assert "error" in json_data, f"Expected 'error' but got {json_data}"
    assert (
        response.status_code == 400
    ), f"Expected 400 but got {response.status_code}: {json_data}"


def test_empty_request(client):
    response = client.post(
        "/api/chat/",
        data=json.dumps({}),
        content_type="application/json",
    )

    json_data = response.get_json()
    assert json_data is not None, "Expected JSON response but got None"

    assert "error" in json_data, f"Expected 'error' but got {json_data}"
    assert (
        response.status_code == 400
    ), f"Expected 400 but got {response.status_code}: {json_data}"
