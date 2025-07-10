# tests/test_llm_service.py

import pytest
from unittest.mock import patch, MagicMock
from rag.app.services.llm import (
    get_llm_response,
    get_gpt_response,
    get_mock_response,
    stream_llm_response,
    generate_embedding,
    generate_prompt,
)
from rag.app.schemas.data import LLMModel, Document
from rag.app.db.connections import MetricsConnection

# ---------------------------------------------------------------
# Dummy MetricsConnection for tests (no DB writes)
# ---------------------------------------------------------------


class DummyMetricsConnection(MetricsConnection):
    def log(self, metric_type: str, data: dict):
        pass

    from contextlib import contextmanager

    @contextmanager
    def timed(self, metric_type: str, data: dict):
        yield


# ---------------------------------------------------------------
# Test get_llm_response (MOCK)
# ---------------------------------------------------------------


def test_get_llm_response_mock():
    metrics = DummyMetricsConnection()
    result = get_llm_response(
        metrics_connection=metrics,
        prompt="Hello world",
        model=LLMModel.MOCK,
    )
    assert isinstance(result, str)
    assert "Lorem ipsum" in result


# ---------------------------------------------------------------
# Test get_llm_response (GPT-4) with patching
# ---------------------------------------------------------------


@patch("rag.app.services.llm.get_gpt_response")
def test_get_llm_response_gpt4(mock_get_gpt_response):
    mock_get_gpt_response.return_value = ("fake response", {"tokens": 10})

    metrics = DummyMetricsConnection()
    result = get_llm_response(
        metrics_connection=metrics,
        prompt="Hello world",
        model=LLMModel.GPT_4,
    )
    assert result == "fake response"
    mock_get_gpt_response.assert_called_once()


# ---------------------------------------------------------------
# Test get_mock_response
# ---------------------------------------------------------------


def test_get_mock_response():
    response, metrics = get_mock_response()
    assert isinstance(response, str)
    assert isinstance(metrics, dict)
    assert "Lorem ipsum" in response


# ---------------------------------------------------------------
# Test get_gpt_response with patched OpenAI client
# ---------------------------------------------------------------


@patch("rag.app.services.llm.get_openai_client")
def test_get_gpt_response_success(mock_get_client):
    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.usage.prompt_tokens = 10
    fake_response.usage.completion_tokens = 5
    fake_response.usage.total_tokens = 15
    fake_response.model = "fake-model"
    fake_response.choices = [
        MagicMock(message=MagicMock(content="This is a test response."))
    ]
    fake_client.chat.completions.create.return_value = fake_response

    mock_get_client.return_value = fake_client

    result, metrics = get_gpt_response(prompt="Test", model="fake-model")

    assert result == "This is a test response."
    assert metrics["prompt_tokens"] == 10
    assert metrics["completion_tokens"] == 5
    assert metrics["total_tokens"] == 15
    assert metrics["model"] == "fake-model"


@patch("rag.app.services.llm.get_openai_client")
def test_get_gpt_response_error(mock_get_client):
    fake_client = MagicMock()
    fake_client.chat.completions.create.side_effect = Exception("fail")

    mock_get_client.return_value = fake_client

    result, metrics = get_gpt_response(prompt="Test", model="fake-model")

    assert "Error" in result
    assert metrics is None


# ---------------------------------------------------------------
# Test stream_llm_response
# ---------------------------------------------------------------


@patch("rag.app.services.llm.get_openai_client")
def test_stream_llm_response(mock_get_client):
    fake_client = MagicMock()

    # Create fake streaming chunks
    chunk1 = MagicMock()
    chunk1.choices = [MagicMock(delta=MagicMock(content="Hello"))]
    chunk2 = MagicMock()
    chunk2.choices = [MagicMock(delta=MagicMock(content=" world"))]

    fake_client.chat.completions.create.return_value = iter([chunk1, chunk2])

    mock_get_client.return_value = fake_client

    metrics = DummyMetricsConnection()
    generator = stream_llm_response(
        metrics_connection=metrics,
        prompt="Test prompt",
        model="fake-model",
    )
    outputs = list(generator)
    assert "Hello" in outputs
    assert " world" in outputs
    assert "[DONE]" in outputs


# ---------------------------------------------------------------
# Test generate_embedding (MOCK)
# ---------------------------------------------------------------


def test_generate_embedding_mock():
    metrics = DummyMetricsConnection()
    embedding = generate_embedding(
        metrics_connection=metrics,
        text="Hello world",
        configuration=LLMModel.MOCK,
    )
    assert isinstance(embedding.vector, list)
    assert len(embedding.vector) == 3
    assert isinstance(embedding.vector[0], float)


# ---------------------------------------------------------------
# Test generate_prompt
# ---------------------------------------------------------------


def test_generate_prompt_basic():
    doc = Document(
        text="This is a test quote.",
        metadata={"source": "Book A", "page": 123},
        vector=[0.1, 0.2, 0.3],
    )
    prompt = generate_prompt(
        user_question="What is the Rav's view on ethics?",
        data=[doc],
    )
    assert "This is a test quote." in prompt
    assert "Book A" in prompt
    assert "What is the Rav's view on ethics?" in prompt
