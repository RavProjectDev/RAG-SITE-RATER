import pytest
import json
from rag_endpoint.rav_api.app import create_app


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_valid_request(client):
    request_body = {"question": "Why did Moshe sacrifice his family life?"}

    response = client.post(
        "api/chat/", data=json.dumps(request_body), content_type="application/json"
    )
    assert response.status_code == 200, "Expected 200 but received {}".format(
        response.status_code
    )
    assert (
        "message" in response.get_json()
    ), "Expected message in response but received {}".format(
        response.get_json()["message"]
    )


def test_invalid_request_format(client):
    request_body = {"not_expected_key": "..."}

    response = client.post(
        "api/chat/", data=json.dumps(request_body), content_type="application/json"
    )

    assert (
        "error" in response.get_json()
    ), f"Expected error but received {response.get_json()}"
    assert (
        response.status_code == 400
    ), f"Expected 400 but received {response.status_code}: {response.get_json()['error']}"


def test_empty_request(client):
    response = client.post(
        "api/chat/", data=json.dumps({}), content_type="application/json"
    )

    assert (
        "error" in response.get_json()
    ), f"Expected error but received {response.get_json()}"
    assert (
        response.status_code == 400
    ), f"Expected 400 but received {response.status_code}: {response.get_json()['error']}"
