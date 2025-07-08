import pytest
from pip._internal.configuration import Configuration

from rag.app.services.embedding import generate_embedding
from rag.app.schemas.data import EmbeddingConfiguration


def test_generate_embedding_bert(monkeypatch):
    monkeypatch.setattr(
        "rag.app.services.embedding.bert_small", lambda text: [1.0, 2.0, 3.0]
    )
    emb = generate_embedding("test", EmbeddingConfiguration.BERT_SMALL)
    assert emb.vector == [1.0, 2.0, 3.0]
    assert emb.text == "test"


def test_generate_embedding_gemini(monkeypatch):
    monkeypatch.setattr(
        "rag.app.services.embedding.gemini_embedding", lambda text: [4.0, 5.0, 6.0]
    )
    emb = generate_embedding("test", EmbeddingConfiguration.GEMINI)
    assert emb.vector == [4.0, 5.0, 6.0]
    assert emb.text == "test"


def test_generate_embedding_invalid():
    with pytest.raises(RuntimeError):
        generate_embedding("test", None)
