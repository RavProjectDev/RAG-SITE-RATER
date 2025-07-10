import uuid
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
import json
import asyncio

from rag.app.services.auth import verify
from rag.app.services.llm import stream_llm_response, generate_prompt, get_llm_response
from rag.app.services.preprocess.user_input import pre_process_user_query
from rag.app.services.embedding import generate_embedding
from rag.app.exceptions import BaseAppException
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


@router.post("/")
async def handler(
    request: Request,
    embedding_conn: EmbeddingConnection = Depends(get_embedding_conn),
    metrics_conn: MetricsConnection = Depends(get_metrics_conn),
    embedding_configuration: EmbeddingConfiguration = Depends(
        get_embedding_configuration
    ),
    llm_configuration: LLMModel = Depends(get_llm_configuration),
):
    """
    Synchronous chat completion endpoint.

    Accepts a JSON payload representing a user event, processes the
    event into a prompt using embeddings and context retrieval, and
    calls the LLM synchronously to produce a single response.

    Request Body (JSON):
    --------------------
    Event payload containing:
        - user query
        - any additional user context

    Returns:
    --------
    JSONResponse:
        {
            "message": <llm response text>,
            "metadata": <list of document metadata used for context>
        }

    Raises:
    -------
    HTTPException (500):
        If the request exceeds the configured timeout or encounters
        an unexpected error.

    HTTPException (400):
        If the incoming event fails validation or processing.
    """
    settings = get_settings()
    event = None
    try:
        # Ensure event is available for error handling
        event = await request.json()

        async def inner_logic():
            prompt, metadata = await generate(
                event,
                request,
                embedding_configuration=embedding_configuration,
                connection=embedding_conn,
            )
            llm_response = get_llm_response(
                metrics_connection=metrics_conn, prompt=prompt, model=llm_configuration
            )
            response = {"message": llm_response, "metadata": metadata}
            return JSONResponse(content=response, status_code=200)

        return await asyncio.wait_for(
            inner_logic(), timeout=settings.external_api_timeout
        )

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=500,
            detail=f"Request timed out after {settings.external_api_timeout} seconds.",
        )
    except BaseAppException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream(
    request: Request,
    embedding_conn: EmbeddingConnection = Depends(get_embedding_conn),
    metrics_conn: MetricsConnection = Depends(get_metrics_conn),
    embedding_configuration: EmbeddingConfiguration = Depends(
        get_embedding_configuration
    ),
    llm_configuration: LLMModel = Depends(get_llm_configuration),
):
    """
    Streaming chat completion endpoint.

    Accepts a JSON payload representing a user event, processes the
    event into a prompt using embeddings and context retrieval, and
    streams the LLM response token-by-token via Server-Sent Events (SSE).

    Each SSE message has the format:
        data: {"data": "<chunk>"}

    The stream concludes with:
        data: [DONE]

    Request Body (JSON):
    --------------------
    Event payload containing:
        - user query
        - any additional user context

    Returns:
    --------
    StreamingResponse:
        Server-sent events streaming the LLM response in small chunks,
        preceded by metadata about the retrieved context.

    Raises:
    -------
    HTTPException (500):
        If the request exceeds the configured timeout or encounters
        an unexpected error.

    HTTPException (400):
        If the incoming event fails validation or processing.
    """
    settings = get_settings()
    event = None
    try:
        event = await request.json()

        async def inner_stream():
            prompt, metadata = await generate(
                event,
                request,
                embedding_configuration=embedding_configuration,
                connection=embedding_conn,
            )

            def event_generator():
                yield f"data: {json.dumps({'metadata': metadata})}\n\n"
                for chunk in stream_llm_response(
                    metrics_connection=metrics_conn, prompt=prompt
                ):
                    yield f"data: {json.dumps({'data': chunk})}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        return await asyncio.wait_for(
            inner_stream(), timeout=settings.external_api_timeout
        )

    except asyncio.TimeoutError:
        return JSONResponse(
            content={
                "error": f"Streaming request timed out after {settings.external_api_timeout} seconds."
            },
            status_code=500,
        )
    except BaseAppException as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


async def generate(
    event,
    request: Request,
    embedding_configuration: EmbeddingConfiguration,
    connection: EmbeddingConnection,
):
    """
    Generate an LLM prompt and retrieve relevant context.

    This function processes an incoming user event:
    - verifies the event's validity
    - extracts and preprocesses the user query
    - generates an embedding vector for the query
    - retrieves similar documents from the vector store
    - creates an LLM prompt incorporating the retrieved context

    Parameters:
    -----------
    event : dict
        JSON payload representing the user event.
    request : Request
        The current FastAPI request object, used to access
        application state (e.g. DB connections).

    Returns:
    --------
    tuple:
        - prompt (str): The generated text prompt to send to the LLM.
        - metadata (list[dict]): Metadata from the documents used for context.

    Raises:
    -------
    BaseAppException:
        If event verification fails or required fields are missing.
    """
    request_id = uuid.uuid4().hex
    result, data_message = verify(event)
    if not result:
        raise BaseAppException(f"Invalid event: {event}")

    user_question: str = pre_process_user_query(data_message)
    vector: list[float] = generate_embedding(
        metrics_connection=request.app.state.metrics_connection,
        text=user_question,
        configuration=embedding_configuration,
    ).vector

    data: list[Document] = connection.retrieve(vector)
    prompt: str = generate_prompt(user_question, data)

    return prompt, [datum.metadata for datum in data]
