from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.params import Path
from motor.motor_asyncio import AsyncIOMotorClient
from starlette import status

from rag.app.db.connections import EmbeddingConnection
from rag.app.dependencies import get_embedding_conn, get_embedding_configuration
from rag.app.exceptions.embedding import EmbeddingException
from rag.app.models.data import DocumentModel
from rag.app.schemas.data import EmbeddingConfiguration
from rag.app.schemas.form import RatingsModel, UploadRatingsRequest
from rag.app.services.embedding import generate_embedding
from rag.app.services.preprocess.user_input import pre_process_user_query

FORM_COLLECTION = "site_data"
router = APIRouter(
    prefix="",
)


@router.get(
    "/{question}",
    response_model=list[DocumentModel],
)
async def get_chunks(
    question: str = Path(...),
    embedding_configuration: EmbeddingConfiguration = Depends(
        get_embedding_configuration
    ),
    connection: EmbeddingConnection = Depends(get_embedding_conn),
) -> list[DocumentModel]:
    # Preprocess question
    cleaned_question = pre_process_user_query(question)

    # Generate embedding with metrics logging
    try:
        embedding = await generate_embedding(
            text=cleaned_question,
            configuration=embedding_configuration,
        )
        vector: list[float] = embedding.vector
        data: list[DocumentModel]
        data = await connection.retrieve(embedded_data=vector)

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    return data


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
        )
        await collection.insert_one(model.to_dict())
    return {"success": True}
