# config.py

from pydantic_settings import BaseSettings
from rag.app.schemas.data import EmbeddingConfiguration


class Settings(BaseSettings):
    openai_api_key: str
    sbert_api_url: str
    mongodb_uri: str
    mongodb_db_name: str
    mongodb_vector_collection: str
    collection_index: str
    gemini_api_key: str
    google_cloud_project_id: str
    embedding_configuration: EmbeddingConfiguration = EmbeddingConfiguration.GEMINI
    vector_path: str = "vector"
    vertex_region: str
    chunk_size: int = 100
    model_config = {"env_file": ".env"}


settings = Settings()
