import time
import uuid
from flask import Blueprint, request, jsonify,Response

from rag_endpoint.rav_api.rav_endpoint.pre_process import pre_process
from rag_endpoint.rav_api.rav_endpoint.llm import prompt_manager, get_llm_response
from rag_endpoint.rav_api.rav_endpoint.exceptions import BaseAppException
from rag_endpoint.rav_api.rav_endpoint.util import verify
from rag_endpoint.rav_api.rav_endpoint.classes import Document

from shared.embedding.embed import embed
from shared.constants import  (
        MONGODB_URI,
        MONGODB_DB_NAME ,
        MONGODB_VECTOR_COLLECTION ,
        COLLECTION_INDEX
)
from shared.db.mongodb_connection import MongoConnection,Connection
from shared.enums import EmbeddingConfiguration
assert MONGODB_URI is not None, "MONGODB_URI environment variable is not set"
assert MONGODB_DB_NAME is not None, "MONGODB_DB_NAME environment variable is not set"
assert MONGODB_VECTOR_COLLECTION is not None, "MONGODB_VECTOR_COLLECTION environment variable is not set"
assert COLLECTION_INDEX is not None, "COLLECTION_INDEX environment variable is not set"

connection: Connection = MongoConnection( 
            uri=MONGODB_URI, 
            collection_name=MONGODB_VECTOR_COLLECTION, 
            index=COLLECTION_INDEX, 
            db_name=MONGODB_DB_NAME
        )
embedding_configuration = EmbeddingConfiguration.GEMINI

        

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

chat_bp = Blueprint("chat", __name__)

def process_user_question(user_question: str) -> str:
    """Pre-process user question"""
    return pre_process(user_question)

def generate_embedding(user_question: str,configuration: EmbeddingConfiguration) -> list[float]:
    """Get vector embedding for user question"""
    vector: list[float] = embed(user_question,configuration=configuration)
    return vector

def retrieve_documents(client: Connection, vector: list[float]) -> list[Document]:
    """Get relevant documents based on embedding"""
    result = client.retrieve(vector)
    return result if result is not None else []

def run_prompt(user_question: str, data: list[Document]) -> str:
    """Generate LLM prompt"""
    return prompt_manager.generate_prompt(
        user_question=user_question, data=data
        )

def get_llm_response_from_generated_prompt(prompt: str): 
    return get_llm_response.run_generated_prompt(
        prompt = prompt,
        model="o4-mini"
    )



@chat_bp.route("/", methods=["POST"])
def handler():
    try:
        event = request.get_json()
        prompt = generate(event)
        llm_response: str = get_llm_response_from_generated_prompt(prompt)
        response = {"message": llm_response}
        return jsonify(response), 200
    except BaseAppException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": "Unexpected server error"}), 400

@chat_bp.route("/stream", methods=["POST"])
def stream():
    try:
        event = request.get_json()
        prompt = generate(event)
        def stream_response():
            yield from get_llm_response.stream_llm_response_from_generated_prompt(prompt)
        return Response(stream_response(), content_type='text/event-stream')
    except BaseAppException as e:
        return jsonify({"error": e.message}), 400
    except Exception as e:
        return jsonify({"error": "Unexpected server error"}), 400

def generate(event):
    request_id = uuid.uuid4().hex
    logger.info(f"[{request_id}] Received event: {event}")
    result, data_message = verify(event)

    if not result:
        raise BaseAppException(f"Invalid event: {event}")

    user_question: str = process_user_question(data_message)
    vector: list[float] = generate_embedding(user_question, embedding_configuration)
    data: list[Document] = retrieve_documents(
        client=connection,
        vector=vector
    )
    prompt: str = run_prompt(user_question, data)
    return prompt