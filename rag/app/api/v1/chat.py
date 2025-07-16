import uuid
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
import json
import asyncio

from rag.app.schemas.requests import ChatRequest, TypeOfRequest
from rag.app.schemas.response import ChatResponse
from rag.app.services.llm import (
    stream_llm_response,
    generate_prompt,
    get_llm_response,
)
from rag.app.services.preprocess.user_input import pre_process_user_query
from rag.app.services.embedding import generate_embedding
from rag.app.exceptions import BaseAppException
from rag.app.schemas.data import (
    Document,
    EmbeddingConfiguration,
    LLMModel,
)
from rag.app.core.config import get_settings
from rag.app.db.connections import EmbeddingConnection, MetricsConnection
from rag.app.dependencies import (
    get_embedding_conn,
    get_metrics_conn,
    get_embedding_configuration,
    get_llm_configuration,
)

router = APIRouter()

@router.post("/", response_model=None)
async def handler(
    chat_request: ChatRequest,
    request: Request,
    embedding_conn: EmbeddingConnection = Depends(get_embedding_conn),
    metrics_conn: MetricsConnection = Depends(get_metrics_conn),
    embedding_configuration: EmbeddingConfiguration = Depends(get_embedding_configuration),
    llm_configuration: LLMModel = Depends(get_llm_configuration),
) -> ChatResponse | StreamingResponse:
    """
    Asynchronous chat completion endpoint for handling streaming and non-streaming chat requests.
    """
    settings = get_settings()

    # Generate prompt and metadata using the provided embedding configuration
    prompt, metadata = await generate(
        chat_request=chat_request,
        request=request,
        embedding_configuration=embedding_configuration,
        connection=embedding_conn,
    )
    if chat_request.type_of_request == TypeOfRequest.STREAM:
        def event_generator():
            """Synchronous generator for Server-Sent Events (SSE)."""
            yield f"data: {json.dumps({'metadata': metadata})}\n\n"
            for chunk in stream_llm_response(
                metrics_connection=metrics_conn,
                prompt=prompt,
            ):
                yield f"data: {json.dumps({'data': chunk})}\n\n"
            yield "data: [DONE]\n\n"

        async def stream_response():
            """Async wrapper for streaming response."""
            return StreamingResponse(event_generator(), media_type="text/event-stream")

        try:
            return await asyncio.wait_for(
                stream_response(),
                timeout=settings.external_api_timeout,
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=500,
                detail=f"Streaming request timed out after {settings.external_api_timeout} seconds.",
            )
        except BaseAppException as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    else:
        async def full_response():
            # Get LLM response
            llm_response = await get_llm_response(
                metrics_connection=metrics_conn,
                prompt=prompt,
                model=llm_configuration,
            )
            # Create and return ChatResponse
            return ChatResponse(
                message=llm_response,
                metadatas=metadata,
            )

        try:
            return await asyncio.wait_for(
                full_response(),
                timeout=settings.external_api_timeout,
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=500,
                detail=f"Request timed out after {settings.external_api_timeout} seconds.",
            )
        except BaseAppException as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")




async def generate(
    chat_request: ChatRequest,
    request: Request,
    embedding_configuration: EmbeddingConfiguration,
    connection: EmbeddingConnection,
):
    """
    Generate an LLM prompt and retrieve relevant context.
    """
    request_id = uuid.uuid4().hex
    # Pull directly from validated model
    user_question: str = chat_request.question
    # Optionally do further verification here if needed:
    if not user_question.strip():
        raise BaseAppException("Question is empty.")

    # Preprocess question
    cleaned_question = pre_process_user_query(user_question)

    # Generate embedding
    embedding=  await generate_embedding(
        metrics_connection=request.app.state.metrics_connection,
        text=cleaned_question,
        configuration=embedding_configuration,
    )

    vector: list[float] = embedding.vector
    # Retrieve matching documents
    data: list[Document] = await connection.retrieve(embedded_data=vector)

    # Generate prompt
    prompt: str = generate_prompt(cleaned_question, data)

    return prompt, [datum.metadata for datum in data]
