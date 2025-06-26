from google.auth import default
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from sentence_transformers import SentenceTransformer
from shared.enums import EmbeddingConfiguration 

bert_small_model = SentenceTransformer("all-MiniLM-L6-v2")
def bert_small(text_data: str) -> list[float]:
    embedding: list[float] = []
    vector: list[float] = bert_small_model.encode(text_data).tolist()
    return vector

def gemini_embedding(text_data: str) -> list[float]:
    credentials, _ = default()
    project = "theravproject"
    region = "northamerica-northeast1"
    task = "RETRIEVAL_DOCUMENT"
    vertexai.init(project=project, location=region, credentials=credentials)
    model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")
    text_input = TextEmbeddingInput(text=text_data, task_type=task)
    vector = model.get_embeddings(
        [text_input],
        output_dimensionality=784
    )
    return vector[0].values
def embed(text: str, configuration: EmbeddingConfiguration) -> list[float]:
    if configuration.value == EmbeddingConfiguration.BERT_SMALL.value:
        return bert_small(text)
    elif configuration.value == EmbeddingConfiguration.GEMINI.value:
        return gemini_embedding(text)
    else:
        raise ValueError(f"Unsupported embedding configuration: {configuration.name}")


