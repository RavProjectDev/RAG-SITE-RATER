import uuid

from fastapi import APIRouter, Request
from motor.motor_asyncio import AsyncIOMotorClient

from rag.app.db.connections import EmbeddingConnection
from rag.app.exceptions.db import DataBaseException
from rag.app.exceptions.embedding import EmbeddingException
from rag.app.models.data import DocumentModel
from rag.app.schemas.data import EmbeddingConfiguration
from rag.app.schemas.form import UploadRatingsRequest, RatingsModel
from rag.app.services.embedding import generate_embedding
from rag.app.services.preprocess.user_input import pre_process_user_query

FORM_COLLECTION = "site_data"
router = APIRouter(
    prefix="/form",
)


@router.get(
    "/",
    response_model=list[DocumentModel],
)
async def get_chunks(
    question: str,
    embedding_configuration: EmbeddingConfiguration,
    connection: EmbeddingConnection,
) -> list[DocumentModel]:
    # Preprocess question
    cleaned_question = pre_process_user_query(question)

    # Generate embedding with metrics logging
    embedding = None
    try:
        embedding = await generate_embedding(
            text=cleaned_question,
            configuration=embedding_configuration,
        )

    except EmbeddingException as e:
        raise e
    except Exception as e:
        raise EmbeddingException(f"Unexpected embedding error: {str(e)}")
    if embedding is None:
        raise EmbeddingException(f"Could not generate embedding for {question}")

    vector: list[float] = embedding.vector
    data: list[DocumentModel]
    try:
        data = await connection.retrieve(embedded_data=vector)
    except DataBaseException as e:
        raise
    except Exception as e:
        raise DataBaseException(f"Database retrieval failed: {str(e)}")

    return data


@router.post(
    "/upload_ratings",
)
async def upload_ratings(request: UploadRatingsRequest, app_state: Request):
    client: AsyncIOMotorClient = app_state.app.state.db_client
    collection = client[FORM_COLLECTION]
    model = RatingsModel(user_question=request.user_question, ratings=request.ratings)
    response = collection.insert_one(model.model_dump())
    if response:
        return True
    return False
