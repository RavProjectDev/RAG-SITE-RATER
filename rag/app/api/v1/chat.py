import uuid
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
import json
import asyncio
from starlette import status

from rag.app.exceptions.base import BaseAppException
from rag.app.exceptions.db import DataBaseException, NoDocumentFoundException
from rag.app.exceptions.embedding import (
    EmbeddingConfigurationException,
    EmbeddingException,
    EmbeddingTimeOutException,
    EmbeddingAPIException,
)
from rag.app.exceptions.validation import InputValidationError
from rag.app.exceptions.llm import (
    LLMBaseException,
)
from rag.app.schemas.requests import ChatRequest, TypeOfRequest
from rag.app.schemas.response import ChatResponse
from rag.app.services.llm import stream_llm_response, generate_prompt, get_llm_response
from rag.app.services.preprocess.user_input import pre_process_user_query
from rag.app.services.embedding import generate_embedding
from rag.app.schemas.data import Document, EmbeddingConfiguration, LLMModel
from rag.app.core.config import get_settings
from rag.app.db.connections import EmbeddingConnection, MetricsConnection
from rag.app.dependencies import (
    get_embedding_conn,
    get_metrics_conn,
    get_embedding_configuration,
    get_llm_configuration,
)

router = APIRouter()


@router.post(
    "/",
    response_model=None,
)
async def handler(
    chat_request: ChatRequest,
    request: Request,
    embedding_conn: EmbeddingConnection = Depends(get_embedding_conn),
    metrics_conn: MetricsConnection = Depends(get_metrics_conn),
    embedding_configuration: EmbeddingConfiguration = Depends(
        get_embedding_configuration
    ),
    llm_configuration: LLMModel = Depends(get_llm_configuration),
) -> ChatResponse | StreamingResponse:
    """
    Asynchronous chat completion endpoint for handling streaming and non-streaming chat requests.

    Args:
        chat_request: The validated chat request model.
        request: The FastAPI request object.
        embedding_conn: Database connection for embeddings.
        metrics_conn: Connection for logging metrics.
        embedding_configuration: Configuration for generating embeddings.
        llm_configuration: LLM model configuration.

    Returns:
        ChatResponse | StreamingResponse: Non-streaming or streaming response.

    Raises:
        HTTPException: For validation, database, embedding, LLM, or unexpected errors.
    """
    settings = get_settings()

    try:
        # Generate prompt and metadata
        prompt, metadata = await asyncio.wait_for(
            generate(
                chat_request=chat_request,
                request=request,
                embedding_configuration=embedding_configuration,
                connection=embedding_conn,
                metrics_connection=metrics_conn,  # Pass metrics_conn for logging
            ),
            timeout=settings.external_api_timeout,
        )
        if chat_request.type_of_request == TypeOfRequest.STREAM:

            async def event_generator():
                """Asynchronous generator for Server-Sent Events (SSE)."""
                yield f"data: {json.dumps({'metadata': metadata})}\n\n"
                async for chunk in stream_llm_response(
                    metrics_connection=metrics_conn,
                    prompt=prompt,
                    model=llm_configuration.value,
                ):
                    yield f"data: {json.dumps({'data': chunk})}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")
        else:

            async def full_response():
                llm_response = await get_llm_response(
                    metrics_connection=metrics_conn,
                    prompt=prompt,
                    model=llm_configuration,
                )
                return ChatResponse(message=llm_response, metadatas=metadata)

        return await full_response()
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Timeout while waiting for chat request",
        )
    except NoDocumentFoundException as e:
        return ChatResponse(metadatas=[], message=e.message_to_ui)
    except BaseAppException as e:
        raise HTTPException(
            status_code=e.status_code, detail={"code": e.code, "error": e.message}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"code": "internal_server_error", "message": str(e)}
        )


async def generate(
    chat_request: ChatRequest,
    request: Request,
    embedding_configuration: EmbeddingConfiguration,
    connection: EmbeddingConnection,
    metrics_connection: MetricsConnection,
) -> (str, list[dict]):
    """
    Generate an LLM prompt and retrieve relevant context.

    Args:
        chat_request: The validated chat request model.
        request: The FastAPI request object.
        embedding_configuration: Configuration for generating embeddings.
        connection: Database connection for retrieving documents.
        metrics_connection: Connection for logging metrics.

    Returns:
        Tuple[str, List[dict]]: The generated prompt and list of metadata.

    Raises:
        InputValidationError: If the user question is empty.
        EmbeddingException: For embedding-related errors.
        DataBaseException: For database retrieval errors.
        LLMException: For prompt generation errors.
    """
    request_id = uuid.uuid4().hex
    user_question: str = chat_request.question

    if not user_question.strip():
        raise InputValidationError("Question is empty.")
    if not isinstance(embedding_configuration, EmbeddingConfiguration):
        raise InputValidationError("Invalid embedding configuration")
    if not isinstance(connection, EmbeddingConnection):
        raise InputValidationError("Invalid embedding connection")
    if not isinstance(metrics_connection, MetricsConnection):
        raise InputValidationError("Invalid metrics connection")

    # Preprocess question
    cleaned_question = pre_process_user_query(user_question)

    # Generate embedding with metrics logging
    embedding = None
    async with metrics_connection.timed(
        metric_type="EMBEDDING", data={"request_id": request_id}
    ):
        try:
            embedding = await generate_embedding(
                metrics_connection=metrics_connection,
                text=cleaned_question,
                configuration=embedding_configuration,
            )

        except (
            EmbeddingException,
            EmbeddingConfigurationException,
            EmbeddingAPIException,
            EmbeddingTimeOutException,
        ) as e:
            raise
        except Exception as e:
            raise EmbeddingException(f"Unexpected embedding error: {str(e)}")

        if embedding is None:
            raise EmbeddingException(
                f"Could not generate embedding for {user_question}"
            )

    # Retrieve matching documents with metrics logging
    vector: list[float] = embedding.vector
    data: list[Document] = []
    async with metrics_connection.timed(
        metric_type="RETRIEVAL", data={"request_id": request_id}
    ):
        try:
            data = await connection.retrieve(
                embedded_data=vector, name_spaces=chat_request.name_spaces
            )
        except DataBaseException as e:
            raise
        except Exception as e:
            raise DataBaseException(f"Database retrieval failed: {str(e)}")

    # Generate prompt
    try:
        prompt = generate_prompt(cleaned_question, data)
        return prompt, [datum.metadata for datum in data]
    except (LLMBaseException, InputValidationError) as e:
        raise
    except Exception as e:
        raise LLMBaseException(f"Prompt generation failed: {str(e)}")
