import httpx

from rag.app.exceptions.upload import SRTFileNotFound
from rag.app.services.preprocess.transcripts import preprocess_raw_transcripts
from rag.app.schemas.data import (
    Chunk,
    VectorEmbedding,
    EmbeddingConfiguration,
    Embedding,
    SanityData,
)
from rag.app.services.embedding import generate_embedding
from rag.app.db.connections import EmbeddingConnection, MetricsConnection
from rag.app.schemas.requests import UploadRequest


async def pre_process_uploaded_documents(
    upload_request: UploadRequest,
    metrics_conn: MetricsConnection,
    embedding_configuration: EmbeddingConfiguration,
) -> list[VectorEmbedding]:
    contents = await fetch_transcript(str(upload_request.transcriptURL))
    chunks = process_transcript_contents(upload_request.title, contents)
    embeddings = await generate_all_embeddings(
        chunks, embedding_configuration, metrics_conn, upload_request
    )
    return embeddings


async def fetch_transcript(transcript_url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(transcript_url)
    if not response.content:
        raise SRTFileNotFound
    return response.content.decode("utf-8")


def process_transcript_contents(title: str, raw_text: str) -> list[Chunk]:
    raw_transcripts = [(title, raw_text)]
    return preprocess_raw_transcripts(raw_transcripts)


async def generate_all_embeddings(
    chunks: list[Chunk],
    configuration: EmbeddingConfiguration,
    metrics_connection: MetricsConnection,
    upload_request: UploadRequest,
) -> list[VectorEmbedding]:
    sanity_data = SanityData(**upload_request.model_dump())
    return await embedding_helper(
        chunks, configuration, metrics_connection, sanity_data
    )


async def embedding_helper(
    chunks: list[Chunk],
    configuration: EmbeddingConfiguration,
    metrics_connection: MetricsConnection,
    sanity_data: SanityData,
) -> list[VectorEmbedding]:
    embeddings = []
    for chunk in chunks:
        data: Embedding = await generate_embedding(
            metrics_connection=metrics_connection,
            text=chunk.text,
            configuration=configuration,
        )
        embeddings.append(
            VectorEmbedding(
                vector=data.vector,
                dimension=len(data.vector),
                data=chunk,
                sanity_data=sanity_data,
            )
        )
    return embeddings
