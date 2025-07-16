import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from rag.app.services.embedding import (
    gemini_embedding,
    generate_embedding,
)
from rag.app.schemas.data import EmbeddingConfiguration, Embedding
from rag.app.db.connections import MetricsConnection

# ---------------------------------------------------------------
# Dummy MetricsConnection
# ---------------------------------------------------------------


class DummyMetricsConnection(MetricsConnection):
    def log(self, metric_type: str, data: dict):
        pass

    from contextlib import contextmanager

    @contextmanager
    def timed(self, metric_type: str, data: dict):
        yield


# ---------------------------------------------------------------
# Check if sentence_transformers is installed
# ---------------------------------------------------------------

bert_available = False
try:
    import sentence_transformers

    bert_available = True
except ImportError:
    pass

# ---------------------------------------------------------------
# Test load_bert_model
# ---------------------------------------------------------------


# ---------------------------------------------------------------
# Test bert_small
# ---------------------------------------------------------------


@pytest.mark.skipif(not bert_available, reason="SentenceTransformers not installed")

# ---------------------------------------------------------------
# Test gemini_embedding
# ---------------------------------------------------------------


@patch("rag.app.services.embedding.vertexai.init")
@patch("rag.app.services.embedding.TextEmbeddingModel.from_pretrained")
@patch("rag.app.services.embedding.default")
@patch("rag.app.services.embedding.get_settings")
def test_gemini_embedding(
    mock_get_settings, mock_default, mock_from_pretrained, mock_vertex_init
):
    fake_settings = MagicMock()
    fake_settings.google_cloud_project_id = "my-project"
    fake_settings.vertex_region = "us-central1"
    mock_get_settings.return_value = fake_settings

    mock_default.return_value = ("fake-credentials", None)

    fake_model = MagicMock()
    fake_embedding = MagicMock()
    fake_embedding.values = [0.5, 0.7, 0.9]
    fake_model.get_embeddings.return_value = [fake_embedding]

    mock_from_pretrained.return_value = fake_model

    result = gemini_embedding("Hello world")

    assert result == [0.5, 0.7, 0.9]
    mock_vertex_init.assert_called_once_with(
        project="my-project", location="us-central1", credentials="fake-credentials"
    )


# ---------------------------------------------------------------
# Test generate_embedding - BERT_SMALL
# ---------------------------------------------------------------


@pytest.mark.skipif(not bert_available, reason="SentenceTransformers not installed")
@patch("rag.app.services.embedding.bert_small", return_value=[1.0, 2.0, 3.0])
def test_generate_embedding_bert_small(mock_bert):
    metrics = DummyMetricsConnection()
    result = generate_embedding(
        metrics_connection=metrics,
        text="test",
        configuration=EmbeddingConfiguration.BERT_SMALL,
    )
    assert isinstance(result, Embedding)
    assert result.vector == [1.0, 2.0, 3.0]
    assert result.text == "test"


# ---------------------------------------------------------------
# Test generate_embedding - GEMINI
# ---------------------------------------------------------------


@patch("rag.app.services.embedding.gemini_embedding", return_value=[4.0, 5.0, 6.0])
def test_generate_embedding_gemini(mock_gemini):
    metrics = DummyMetricsConnection()
    result = generate_embedding(
        metrics_connection=metrics,
        text="test",
        configuration=EmbeddingConfiguration.GEMINI,
    )
    assert isinstance(result, Embedding)
    assert result.vector == [4.0, 5.0, 6.0]
    assert result.text == "test"


# ---------------------------------------------------------------
# Test generate_embedding - MOCK
# ---------------------------------------------------------------


def test_generate_embedding_mock():
    metrics = DummyMetricsConnection()
    result = generate_embedding(
        metrics_connection=metrics,
        text="test",
        configuration=EmbeddingConfiguration.MOCK,
    )
    assert isinstance(result, Embedding)
    assert isinstance(result.vector, list)
    assert len(result.vector) == 3
    assert result.text == "test"


# ---------------------------------------------------------------
# Test generate_embedding - Invalid config
# ---------------------------------------------------------------


def test_generate_embedding_invalid_enum():
    metrics = DummyMetricsConnection()

    class DummyEnum:
        value = "dummy"
        name = "dummy"

    with pytest.raises(ValueError):
        generate_embedding(
            metrics_connection=metrics,
            text="test",
            configuration=DummyEnum(),
        )
