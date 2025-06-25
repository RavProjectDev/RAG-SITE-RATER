import os
from dotenv import load_dotenv
load_dotenv()
import logging
from typing import cast

from pymongo import MongoClient
from pymongo.collection import Collection
from rav_endpoint.classes import Document, Embedding
from rav_endpoint.util import timing_decorator

logger = logging.getLogger()
logger.setLevel(logging.INFO)
num_documents = 5

@timing_decorator
def get_relevant_documents(embedding: Embedding, request_id: str, k: int = num_documents) -> list[Document]:
    logger.info(f"[{request_id}] Fetching {k} relevant documents from MongoDB")
    vector: list[float] = embedding.vector
    try:
        collection_driver = mongo_db_initiate_connection(request_id)
        
        query = mongo_query(vector, k, request_id)
        
        logger.info(f"[{request_id}] Executing MongoDB vector search query")
        results = list(collection_driver.aggregate(query))
        logger.info(f"[{request_id}] Retrieved {len(results)} documents")
        
        documents: list[Document] = []
        for result in results:
            document = Document(
                text=str(result.get("text")),
                vector=cast(list[float], result["vector"]),
                metadata=cast(dict[str, object], result["metadata"]),
            )
            documents.append(document)
        
        return documents
        
    except Exception as e:
        logger.error(f"[{request_id}] Document retrieval failed: {e}", exc_info=True)
        raise

def mongo_db_initiate_connection(request_id: str) -> Collection[dict[str, object]]:
    uri = os.environ["MONGODB_URI"]
    db_name = os.environ["MONGODB_DB"]
    collection_name = os.environ["MONGODB_VECTOR_COLLECTION"]
    logger.info(f"[{request_id}] Connecting to MongoDB: DB={db_name}, Collection={collection_name}")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000, socketTimeoutMS=5000,tls=True)
        db = client[db_name]
        collection = db[collection_name]
        return collection
    except Exception as e:
        logger.error(f"[{request_id}] MongoDB connection setup failed: {e}")
        raise

def mongo_query(query_vector: list[float], k: int, request_id: str) -> list:
    vector_index = os.environ["COLLECTION_INDEX"]
    logger.info(f"[{request_id}] Constructing vector search query: k={k}, index={vector_index}")
    pipeline = [
        {
            "$vectorSearch": {
                "queryVector": query_vector,
                "path": "vector",
                "numCandidates": 50,
                "limit": int(k),
                "index": vector_index,
            }
        }
    ]
    return pipeline
