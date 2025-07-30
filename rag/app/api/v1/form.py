import random

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.params import Path
from motor.motor_asyncio import AsyncIOMotorClient
from starlette import status

from rag.app.db.connections import EmbeddingConnection
from rag.app.db.mongodb_connection import MongoEmbeddingStore
from rag.app.dependencies import get_embedding_conn, get_embedding_configuration
from rag.app.exceptions.embedding import EmbeddingException
from rag.app.models.data import DocumentModel
from rag.app.schemas.data import EmbeddingConfiguration
from rag.app.schemas.form import RatingsModel, UploadRatingsRequest
from rag.app.schemas.response import FormGetChunksResponse
from rag.app.services.embedding import generate_embedding
from rag.app.services.preprocess.user_input import pre_process_user_query
from rag.app.core.config import COLLECTIONS, get_settings

FORM_COLLECTION = "site_data"
router = APIRouter(
    prefix="",
)


@router.get(
    "/{question}",
    response_model=FormGetChunksResponse,
)
async def get_chunks(
    app_state: Request,
    question: str = Path(...),
    embedding_configuration: EmbeddingConfiguration = Depends(
        get_embedding_configuration
    ),
    connection: EmbeddingConnection = Depends(get_embedding_conn),
) -> FormGetChunksResponse:
    # Preprocess question
    client: AsyncIOMotorClient = app_state.app.state.db_client
    collection_name = random.choice(COLLECTIONS)
    collection = client[collection_name]
    connection: EmbeddingConnection = MongoEmbeddingStore(
        collection=collection,
        index=get_settings().collection_index,
        vector_path=get_settings().vector_path,
    )
    cleaned_question = pre_process_user_query(question)
    # Generate embedding with metrics logging
    try:
        embedding = await generate_embedding(
            text=cleaned_question,
            configuration=embedding_configuration,
        )
        vector: list[float] = embedding.vector
        data: list[DocumentModel]
        data = await connection.retrieve(embedded_data=vector, threshold=0.85)

    except EmbeddingException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": str(e.message),
                "code": e.code,
                "description": e.description,
            },
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

    return FormGetChunksResponse(
        documents=data,
        embedding_type=collection_name,
    )


@router.post(
    "/upload_ratings",
)
async def upload_ratings(request: UploadRatingsRequest, app_state: Request):
    client: AsyncIOMotorClient = app_state.app.state.db_client
    collection = client[FORM_COLLECTION]
    for data in request.data:
        model = RatingsModel(
            user_question=request.user_question,
            ratings=data,
            embedding_type=request.embedding_type,
        )
        await collection.insert_one(model.to_dict())
    return {"success": True}
