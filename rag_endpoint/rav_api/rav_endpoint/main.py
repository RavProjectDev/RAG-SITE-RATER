import time
import uuid
from flask import Blueprint, request, jsonify

from rav_api.rav_endpoint.pre_process import pre_process
from rav_api.rav_endpoint.llm import prompt_manager, get_llm_response
from rav_api.rav_endpoint.exceptions import BaseAppException
from rav_api.rav_endpoint.util import verify

from shared.embedding.embed import embed
from shared.constants import  (
        MONGO_URI,
        MONGO_DB_NAME ,
        MONGO_COLLECTION ,
        MONGO_INDEX
)
from shared.db.mongodb_connection import MongoConnection,Connection
from shared.enums import EmbeddingConfiguration
from shared.classes import Embedding, Document

connection: Connection = MongoConnection( 
            uri=MONGO_URI, 
            collection_name=MONGO_COLLECTION, 
            index=MONGO_INDEX, 
            db_name=MONGO_DB_NAME
        )
embedding_configuration = EmbeddingConfiguration.GEMINI

        

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

chat_bp = Blueprint("chat", __name__)

def process_user_question(user_question: str) -> str:
    """Pre-process user question"""
    return pre_process(user_question)

def generate_embedding(user_question: str,configuration: EmbeddingConfiguration) -> Embedding:
    """Get vector embedding for user question"""
    return embed([user_question],configuration=configuration)

def retrieve_documents(client: Connection, vector: list[float]) -> list[Document]:
    """Get relevant documents based on embedding"""
    return client.retrieve(vector)

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
    request_start_time = time.time()
    event = request.get_json()
    request_id = uuid.uuid4().hex
    logger.info(f"[{request_id}] Received event: {event}")
    
    try:
        result, data_message = verify(event)
        
        if not result:
            total_time = time.time() - request_start_time
            logger.info(f"[{request_id}] [TIMING] Request failed validation after {total_time:.4f} seconds")
            return jsonify({"error": data_message}) , 400

        user_question: str = process_user_question(data_message)
        vector: list[float] = generate_embedding(user_question,embedding_configuration)
        data: list[Document] = retrieve_documents(
            client=connection, 
            vector=vector
        )
        prompt: str = run_prompt(user_question, data)
        llm_response: str = get_llm_response_from_generated_prompt(prompt)

        response = {"message": llm_response}
        total_time = time.time() - request_start_time
        logger.info(f"[{request_id}] [TIMING] Total request processing completed in {total_time:.4f} seconds")
        
        return jsonify(response), 200

    except BaseAppException as e:
        total_time = time.time() - request_start_time
        logger.error(f"[{request_id}] [TIMING] Request failed with BaseAppException after {total_time:.4f} seconds: {e.message}")
        return jsonify({"error": e.message}), 400
    except Exception as e:
        total_time = time.time() - request_start_time
        logger.error(f"[{request_id}] [TIMING] Request failed with unexpected error after {total_time:.4f} seconds: {e}", exc_info=True)
        return jsonify({"error": "Unexpected server error"}), 400
