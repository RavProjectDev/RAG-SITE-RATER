from google.auth import default
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from rag.app.schemas.data import EmbeddingConfiguration, Embedding
from functools import lru_cache
from rag.app.core.config import settings

@lru_cache()
def load_bert_model():
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError:
        raise ImportError(
            "sentence-transformers is required for BERT_SMALL embedding but is not installed."
        )
    return SentenceTransformer("all-MiniLM-L6-v2")


def bert_small(text_data: str) -> list[float]:
    model = load_bert_model()
    vector = model.encode(text_data).tolist()
    return vector


def gemini_embedding(text_data: str) -> list[float]:
    credentials, _ = default()
    project = settings.google_cloud_project_id
    region = settings.vertex_region
    task = "RETRIEVAL_DOCUMENT"

    vertexai.init(project=project, location=region, credentials=credentials)
    model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")
    text_input = TextEmbeddingInput(text=text_data, task_type=task)
    vector = model.get_embeddings([text_input], output_dimensionality=784)
    return vector[0].values


def generate_embedding(text: str, configuration: EmbeddingConfiguration) -> Embedding:
    if configuration == EmbeddingConfiguration.BERT_SMALL:
        vector = bert_small(text)
    elif configuration == EmbeddingConfiguration.GEMINI:
        vector = gemini_embedding(text)
    else:
        raise ValueError(f"Unsupported embedding configuration: {configuration.name}")

    return Embedding(text=text, vector=vector)
