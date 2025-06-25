from google.auth import default
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from sentence_transformers import SentenceTransformer
from shared.enums import EmbeddingConfiguration 
from shared.logger_config import embedding_logger

bert_small_model = SentenceTransformer("all-MiniLM-L6-v2")
def bert_small(text_data: list[str]) -> list[tuple[str,list[float]]]:
    embedding_logger.info(f"Starting BERT small embedding for {len(text_data)} chunks")
    embeddings: list[tuple[str,list[float]]] = []
    for i, text in enumerate(text_data, 1):
        if i % 100 == 0: 
            embedding_logger.debug(f"Generated {i}/{len(text_data)} embeddings")
        vector: list[float] = bert_small_model.encode(text_data).tolist()
        embeddings.append((text,vector))
    
    embedding_logger.info(f"BERT small embedding completed: {len(embeddings)} embeddings generated")
    return embeddings

def gemini_embedding(text_data: list[str]) -> list[tuple[str,list[float]]]:

    credentials, _ = default()
    project = "theravproject"
    region = "northamerica-northeast1"
    task = "RETRIEVAL_DOCUMENT"
    vertexai.init(project=project, location=region, credentials=credentials)
    model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")
    embeddings: list[tuple[str,list[float]]] = []

    for text in text_data:
        text_input = TextEmbeddingInput(text=text, task_type=task)
        vector = model.get_embeddings(
            [text_input],
            output_dimensionality=784
        )
        embeddings.append((text,vector[0].values))
    return embeddings
def embed(data: list[str], configuration: EmbeddingConfiguration) -> list[tuple[str,list[float]]]:
    embedding_logger.info(f"Starting embedding process with configuration: {configuration.name}")
    if configuration.value == EmbeddingConfiguration.BERT_SMALL.value:
        return bert_small(data)
    elif configuration.value == EmbeddingConfiguration.GEMINI.value:
        return gemini_embedding(data)
    else:
        embedding_logger.error(f"Unsupported embedding configuration: {configuration.name}")
        raise ValueError(f"Unsupported embedding configuration: {configuration.name}")


