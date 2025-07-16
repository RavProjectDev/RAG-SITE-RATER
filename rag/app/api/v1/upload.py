import json

import httpx

from fastapi import APIRouter, Request, Depends, HTTPException, status
from starlette.responses import JSONResponse

from rag.app.schemas.response import UploadResponse
from rag.app.services.preprocess.transcripts import preprocess_raw_transcripts
from rag.app.schemas.data import (
    Chunk,
    VectorEmbedding,
    EmbeddingConfiguration,
    Embedding,
)
from rag.app.services.embedding import generate_embedding

from rag.app.db.connections import EmbeddingConnection, MetricsConnection
from rag.app.dependencies import (
    get_embedding_conn,
    get_metrics_conn,
    get_embedding_configuration,
)
from rag.app.schemas.requests import UploadRequest

router = APIRouter()


@router.post("/")
async def upload_files(
    request: Request,
    embedding_conn: EmbeddingConnection = Depends(get_embedding_conn),
    metrics_conn: MetricsConnection = Depends(get_metrics_conn),
    embedding_configuration: EmbeddingConfiguration = Depends(
        get_embedding_configuration
    ),
):
    """
      Upload endpoint for subtitle (.srt) files.

      Accepts multiple .srt files via multipart/form-data, processes
      their textual content into data chunks, generates vector embeddings
      for each chunk, and stores the embeddings in the database.

      Request:
      --------
    b'{"_id":"55806772-3246-4eaf-88a3-4448eb39846e","_updatedAt":"2025-07-15T20:31:24Z","slug":"kedusha-and-malchus","title":"Kedusha and Malchus","transcriptURL":"https://cdn.sanity.io/files/ybwh5ic4/primary/2fbb38de4c27f54dfe767841cde0dae92c4be543.srt"}'
      Response:
      ---------
      JSON object containing:
          {
              "results": [
                  {
                      "vector": [...],
                      "dimension": <int>,
                      "data": {
                          "text": <str>,
                          ...
                      }
                  },
                  ...
              ]
          }

      Raises:
      -------
      HTTPException (400):
          If any uploaded file is not an .srt file.

      HTTPException (500):
          For any unexpected server-side errors.
    """
    raw = await request.body()  # b'...'
    data = json.loads(raw.decode())  # dict
    parsed: UploadRequest = UploadRequest(**data)
    if not str(parsed.transcriptURL).lower().endswith(".srt"):
        return JSONResponse(
            status_code=400,
            content={
                "detail": f"Uploaded file {parsed.transcriptURL} must be an .srt file"
            },
        )
    contents = None
    async with httpx.AsyncClient() as client:
        response = await client.get(str(parsed.transcriptURL))
        contents = response.content
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not find .srt file",
        )
    text = contents.decode("utf-8")

    raw_transcripts = [(parsed.title, text)]
    # Preprocess raw text into chunks
    chunks = preprocess_raw_transcripts(raw_transcripts)
    # Generate embeddings for each chunk
    embeddings = await embedding_helper(
        chunks=chunks,
        configuration=embedding_configuration,
        metrics_connection=metrics_conn,
    )
    await embedding_conn.insert(embeddings)
    return UploadResponse(message="Uploaded file successfully")


async def embedding_helper(
    chunks: list[Chunk],
    configuration: EmbeddingConfiguration,
    metrics_connection: MetricsConnection,
) -> list[VectorEmbedding]:
    """
    Generate vector embeddings for a list of text chunks.

    Parameters:
    -----------
    chunks : list[Chunk]
        List of text chunks to embed.
    configuration : EmbeddingConfiguration, optional
        The embedding model to use (default: GEMINI).

    Returns:
    --------
    list[VectorEmbedding]
        List of vector embeddings, each containing:
            - vector: list of floats
            - dimension: length of vector
            - data: original Chunk data
    """
    embeddings: list[VectorEmbedding] = []
    for chunk in chunks:
        data: Embedding = await generate_embedding(
            metrics_connection=metrics_connection,
            text=chunk.text,
            configuration=configuration,
        )
        vector = data.vector
        embeddings.append(
            VectorEmbedding(vector=vector, dimension=len(vector), data=chunk)
        )
    return embeddings
