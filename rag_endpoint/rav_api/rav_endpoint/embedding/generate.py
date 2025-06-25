import os
import requests
from rav_endpoint.classes import Embedding
from rav_endpoint.util import timing_decorator
import logging

from google.auth import default
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@timing_decorator
def get_vector_embedding(text: str, request_id: str) -> Embedding:
    logger.info(f"[{request_id}] Getting vector embedding for input text")
    try:
        vec: list[float] = fetch_from_modal_endpoint(text, request_id)
        return Embedding(text=text, vector=vec)
    except Exception as e:
        logger.error(f"[{request_id}] Vector embedding generation failed: {e}", exc_info=True)
        raise


def fetch_from_modal_endpoint(text: str, request_id: str) -> list[float]:
    url = os.environ["SBERT_API_URL"]
    logger.info(f"[{request_id}] Sending request to SBERT endpoint at {url}")
    try:
        res = requests.post(url, json={"text": text}, timeout=20)
        res.raise_for_status()
        embedding = res.json()["embedding"]
        return embedding
    except Exception as e:
        logger.error(f"[{request_id}] SBERT API call failed: {e}", exc_info=True)
        raise


@timing_decorator
def generate_embedding_with_gemini(text: str, request_id: str) -> Embedding:
    logger.info(f"[{request_id}] Getting vector embedding for input text")
    try:
        vec: list[float] = fetch_from_gemini(text, request_id)
        logger.info(f"[{request_id}] Successfully generated embedding of length {len(vec)}")
        return Embedding(text=text, vector=vec)
    except Exception as e:
        logger.error(f"[{request_id}] Vector embedding generation failed: {e}", exc_info=True)
        raise

def fetch_from_gemini(text: str, request_id: str) -> list[float]:
    logger.info(f"[{request_id}] Initializing Vertex AI client")
    try:
        credentials, _ = default()
        project = "theravproject"
        region = "northamerica-northeast1"
        task = "RETRIEVAL_DOCUMENT"

        vertexai.init(project=project, location=region, credentials=credentials)
        logger.info(f"[{request_id}] Vertex AI initialized with project {project} and region {region}")

        model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")
        logger.info(f"[{request_id}] Loaded model 'gemini-embedding-001'")

        text_input = TextEmbeddingInput(text=text, task_type=task)
        vector = model.get_embeddings([text_input], output_dimensionality=784)
        logger.info(f"[{request_id}] Received embedding vector of length {len(vector[0].values)}")

        return vector[0].values
    except Exception as e:
        logger.error(f"[{request_id}] Failed during fetch_from_gemini: {e}", exc_info=True)
        raise