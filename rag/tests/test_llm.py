from rag.app.services.llm import get_llm_response, stream_llm_response, generate_prompt
from rag.app.schemas.data import Document, LLMModel
from unittest.mock import patch, MagicMock


def test_get_llm_response(monkeypatch):
    class DummyResponse:
        class Usage:
            prompt_tokens = 1
            completion_tokens = 1
            total_tokens = 2

        usage = Usage()
        model = "mock"

        class Choice:
            class Message:
                content = "answer"

            message = Message()

        choices = [Choice()]

    monkeypatch.setattr(
        "rag.app.services.llm.client.chat.completions.create",
        lambda **kwargs: DummyResponse(),
    )
    result = get_llm_response("prompt", LLMModel.GPT_4)
    assert result == "answer"


def test_stream_llm_response(monkeypatch):
    dummy_chunk = MagicMock()
    dummy_chunk.choices = [MagicMock(delta=MagicMock(content="abc"))]
    monkeypatch.setattr(
        "rag.app.services.llm.client.chat.completions.create",
        lambda **kwargs: [dummy_chunk],
    )
    chunks = list(stream_llm_response("prompt"))
    assert any("abc" in c for c in chunks)


def test_generate_prompt():
    docs = [
        Document(text="quote", metadata={"source": "book", "page": 1}, vector=[0.1])
    ]
    prompt = generate_prompt("What is Torah?", docs)
    assert "quote" in prompt
    assert "What is Torah?" in prompt
