from google.auth import default
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from rag.app.schemas.data import EmbeddingConfiguration, Embedding
from functools import lru_cache
from rag.app.core.config import get_settings
from rag.app.db.connections import MetricsConnection
import random
from rag.app.exceptions import EmbeddingError
import concurrent.futures


async def gemini_embedding(text_data: str) -> list[float]:
    credentials, _ = default()
    settings = get_settings()
    project = settings.google_cloud_project_id
    region = settings.vertex_region
    task = "RETRIEVAL_DOCUMENT"

    vertexai.init(project=project, location=region, credentials=credentials)
    model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")
    text_input = TextEmbeddingInput(text=text_data, task_type=task)

    def call_model():
        return model.get_embeddings([text_input], output_dimensionality=784)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(call_model)
        try:
            vector = future.result(timeout=10)
            return vector[0].values
        except concurrent.futures.TimeoutError:
            raise EmbeddingError("Gemini embedding timed out.")
        except Exception as e:
            raise EmbeddingError(f"Gemini embedding failed: {str(e)}")


async def generate_embedding(
    metrics_connection: MetricsConnection,
    text: str,
    configuration: EmbeddingConfiguration,
) -> Embedding:
    data = {"embedding_type": configuration.value}
    if configuration is None:
        raise RuntimeError(f"Unknown configuration")

    with metrics_connection.timed(metric_type="embedding", data=data):
        if configuration == EmbeddingConfiguration.GEMINI:
            vector = await gemini_embedding(text)
        elif configuration == EmbeddingConfiguration.MOCK:
            return Embedding(
                text=text, vector=[random.uniform(-1, 1) for _ in range(3)]
            )
        else:
            raise ValueError(
                f"Unsupported embedding configuration: {configuration.name}"
            )

        return Embedding(text=text, vector=vector)
