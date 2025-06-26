from shared.embedding.embed import embed
from shared.classes import VectorEmbedding,Chunk
from shared.enums import EmbeddingConfiguration
from shared.logger_config import embedding_logger,timing_decorator

@timing_decorator(embedding_logger)
def embedding_helper(chunks: list[Chunk],configuration: EmbeddingConfiguration) -> list[VectorEmbedding]:
    embedding_logger.info(f"Starting embedding with configuration: {configuration.name}, for {len(chunks)} chunks")
    embeddings: list[VectorEmbedding] = []
    for chunk in chunks:
          vector: list[float] = embed(chunk.text,configuration)
          embeddings.append(
              VectorEmbedding(
                vector=vector,
                dimension=len(vector),
                data = chunk
              )
          )
    return embeddings