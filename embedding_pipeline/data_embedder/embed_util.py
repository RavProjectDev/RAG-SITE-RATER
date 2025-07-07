from shared.embedding.embed import embed
from shared.classes import VectorEmbedding, Chunk
from shared.enums import EmbeddingConfiguration
from logging import getLogger

logger = getLogger(__name__)


def embedding_helper(
    chunks: list[Chunk], configuration: EmbeddingConfiguration
) -> list[VectorEmbedding]:
    logger.info(
        f"Starting embedding with configuration: {configuration.name}, for {len(chunks)} chunks"
    )
    embeddings: list[VectorEmbedding] = []
    for chunk in chunks:
        vector: list[float] = embed(chunk.text, configuration)
        embeddings.append(
            VectorEmbedding(vector=vector, dimension=len(vector), data=chunk)
        )
    logger.info(f"Finished embedding with configuration: {configuration.name}")
    return embeddings
