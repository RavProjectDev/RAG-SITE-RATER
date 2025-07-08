from rag.app.services.auth import verify


def test_verify_valid():
    event = {"question": "What is Torah?"}
    result, msg = verify(event)
    assert result is True
    assert msg == "What is Torah?"


def test_verify_missing_question():
    event = {}
    result, msg = verify(event)
    assert result is False
    assert "body needs to include question" in msg


def test_verify_json_error():
    # Simulate JSONDecodeError by passing a non-dict
    result, msg = verify(None)
    assert result is False
