from fastapi import UploadFile, File, HTTPException, APIRouter, Request, Depends
from starlette.responses import JSONResponse

from rag.app.services.preprocess.transcripts import preprocess_raw_transcripts
from rag.app.schemas.data import Chunk, VectorEmbedding, EmbeddingConfiguration
from rag.app.services.embedding import generate_embedding

from rag.app.db.connections import EmbeddingConnection, MetricsConnection
from rag.app.dependencies import (
    get_embedding_conn,
    get_metrics_conn,
    get_embedding_configuration,
)

router = APIRouter()


@router.post("/")
async def upload_files(
    request: Request,
    files: list[UploadFile] = File(...),
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
    Multipart form-data with one or more files:
        files: list of .srt files

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
    try:
        raw_transcripts: list[tuple[str, str]] = []
        for file in files:
            if not file.filename.lower().endswith(".srt"):
                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": f"Uploaded file {file.filename} must be an .srt file"
                    },
                )
            contents = await file.read()
            text = contents.decode("utf-8")
            file_name = file.filename
            raw_transcripts.append((file_name, text))

        # Preprocess raw text into chunks
        chunks = preprocess_raw_transcripts(raw_transcripts)

        # Generate embeddings for each chunk
        embeddings = embedding_helper(
            chunks=chunks,
            configuration=embedding_configuration,
            metrics_connection=metrics_conn,
        )
        embedding_conn.insert(embeddings)

        return {"results": embeddings}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def embedding_helper(
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
        vector: list[float] = generate_embedding(
            metrics_connection=metrics_connection,
            text=chunk.text,
            configuration=configuration,
        ).vector
        embeddings.append(
            VectorEmbedding(vector=vector, dimension=len(vector), data=chunk)
        )
    return embeddings
