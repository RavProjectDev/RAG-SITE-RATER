import uuid
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import json

from rag.app.services.auth import verify
from rag.app.services.llm import stream_llm_response, generate_prompt, get_llm_response
from rag.app.services.preprocess.user_input import pre_process_user_query
from rag.app.services.embedding import generate_embedding
from rag.app.exceptions import BaseAppException
from rag.app.schemas.data import Document
from rag.app.core.config import settings
from rag.app.db.connection import Connection

router = APIRouter()


@router.post("/")
async def handler(request: Request):
    try:
        event = await request.json()
        prompt, metadata = await generate(event, request)
        llm_response: str = get_llm_response(prompt)
        response = {"message": llm_response, "metadata": metadata}
        return JSONResponse(content=response, status_code=200)
    except BaseAppException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream(request: Request):
    try:
        event = await request.json()
        prompt, metadata = await generate(event, request)

        def event_generator():
            yield f"data: {json.dumps({'metadata': metadata})}\n\n"
            for chunk in stream_llm_response(prompt):
                yield f"data: {json.dumps({'data': chunk})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except BaseAppException as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


async def generate(event, request: Request):
    request_id = uuid.uuid4().hex
    result, data_message = verify(event)
    if not result:
        raise BaseAppException(f"Invalid event: {event}")

    user_question: str = pre_process_user_query(data_message)
    embedding_configuration = settings.embedding_configuration
    connection: Connection = request.app.state.mongo_conn

    vector: list[float] = generate_embedding(
        user_question, embedding_configuration
    ).vector
    data: list[Document] = connection.retrieve(vector)
    prompt: str = generate_prompt(user_question, data)

    return prompt, [datum.metadata for datum in data]
