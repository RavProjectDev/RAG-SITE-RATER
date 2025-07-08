from fastapi import UploadFile, File, HTTPException, APIRouter, Request, Response
from starlette.responses import JSONResponse

from rag.app.services.preprocess.transcripts import preprocess_raw_transcripts
from rag.app.schemas.data import Chunk, VectorEmbedding, EmbeddingConfiguration
from rag.app.services.embedding import generate_embedding

router = APIRouter()


@router.post("/")
async def upload_files(request: Request, files: list[UploadFile] = File(...)):
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
        processed = preprocess_raw_transcripts(raw_transcripts)
        embeddings = embedding_helper(processed)
        connection = request.app.state.mongo_conn
        connection.insert(embeddings)
        return {"results": embeddings}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def embedding_helper(
    chunks: list[Chunk],
    configuration: EmbeddingConfiguration = EmbeddingConfiguration.GEMINI,
) -> list[VectorEmbedding]:

    embeddings: list[VectorEmbedding] = []
    for chunk in chunks:
        vector: list[float] = generate_embedding(chunk.text, configuration).vector
        embeddings.append(
            VectorEmbedding(vector=vector, dimension=len(vector), data=chunk)
        )
    return embeddings
