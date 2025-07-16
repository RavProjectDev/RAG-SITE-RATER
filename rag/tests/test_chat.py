import pytest
pytestmark = pytest.mark.asyncio
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager
from unittest.mock import patch, MagicMock
from rag.app.main import app
from rag.app.schemas.requests import ChatRequest,TypeOfRequest


@pytest.fixture(autouse=True)
def patch_get_settings(monkeypatch):
    from rag.app.core import config
    from rag.app.core.config import Environment, EmbeddingConfiguration, LLMModel

    fake_settings = MagicMock()
    fake_settings.environment = Environment.TEST
    fake_settings.openai_api_key = "sk-test"
    fake_settings.sbert_api_url = "http://localhost"
    fake_settings.mongodb_uri = "mongodb://localhost:27017"
    fake_settings.mongodb_db_name = "testdb"
    fake_settings.mongodb_vector_collection = "test_vectors"
    fake_settings.collection_index = "test_index"
    fake_settings.vector_path = "vector"
    fake_settings.metrics_collection = "metrics"
    fake_settings.external_api_timeout = 10
    fake_settings.embedding_configuration = EmbeddingConfiguration.MOCK
    fake_settings.llm_configuration = LLMModel.MOCK

    monkeypatch.setattr(config, "get_settings", lambda: fake_settings)


@pytest.mark.asyncio
@patch("rag.app.api.v1.chat.get_llm_response", return_value="Mocked response")
@patch("rag.app.api.v1.chat.pre_process_user_query", return_value="Processed")
@patch("rag.app.api.v1.chat.generate_embedding")
async def test_chat_handler(mock_embed, mock_preprocess, mock_llm):
    mock_embed.return_value.vector = [0.1] * 784

    # override dependencies
    mock_conn = MagicMock()
    mock_conn.retrieve.return_value = []

    app.dependency_overrides = {}
    payload = ChatRequest(
        question  ="What is Torah?",
        type_of_request=TypeOfRequest.FULL.value
    )
    async with LifespanManager(app):
        transport = ASGITransport(app=app)  # pass your FastAPI app here
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/chat/", json=payload.model_dump())
            assert response.status_code == 200
            response = await client.post("/api/v1/chat/", json=payload.model_dump())
            assert response.status_code == 200
            body = response.json()
            assert body["message"] == "Mocked response"
            assert isinstance(body["metadatas"], list)




@pytest.mark.asyncio
@patch("rag.app.api.v1.chat.get_llm_response", return_value="Mocked response")
@patch("rag.app.api.v1.chat.pre_process_user_query", return_value="Processed")
@patch("rag.app.api.v1.chat.generate_embedding")
async def test_chat_fail(mock_embed, mock_preprocess, mock_llm):
    mock_embed.return_value.vector = [0.1] * 732

    # override dependencies
    mock_conn = MagicMock()
    mock_conn.retrieve.return_value = []

    app.dependency_overrides = {}
    payload = ChatRequest(
        question  ="What is Torah?",
        type_of_request=TypeOfRequest.FULL.value
    )
    async with LifespanManager(app):
        transport = ASGITransport(app=app)  # pass your FastAPI app here
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/v1/chat/", json=payload.model_dump())
            assert response.status_code == 200
            response = await client.post("/api/v1/chat/", json=payload.model_dump())
            assert response.status_code == 200
            body = response.json()
            assert body["message"] == "Mocked response"
            assert isinstance(body["metadatas"], list)
