from pymongo import MongoClient
from typing import cast
import certifi
from dataclasses import asdict
from shared.classes import Embedding, Document, VectorEmbedding
from shared.db.connection import Connection
from shared.logger_config import db_logger, timing_decorator
from shared.constants import NUMBER_OF_DOCUMENTS_TO_RETRIEVE,VECTOR_PATH


class MongoConnection(Connection):
    def __init__(self, uri: str, db_name: str, collection_name: str,index: str):
        db_logger.info(f"Initializing MongoDB connection to database: {db_name}, collection: {collection_name}")
        try:
            self.vector_path = VECTOR_PATH
            self.client = MongoClient(uri, tlsCAFile=certifi.where())
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            self.index = index
            db_logger.info("MongoDB connection initialized successfully")
        except Exception as e:
            db_logger.error(f"Failed to initialize MongoDB connection: {str(e)}")
            raise
    @timing_decorator(db_logger)
    def insert(self, embedded_data: list[VectorEmbedding]):
        db_logger.info(f"Preparing to insert {len(embedded_data)} embeddings into MongoDB")
        try:
            documents = [emb.to_dict() for emb in embedded_data]
            if documents:
                db_logger.debug(f"Inserting {len(documents)} documents into MongoDB collection")
                self.collection.insert_many(documents)
                db_logger.info(f"Successfully inserted {len(documents)} documents into MongoDB")
            else:
                db_logger.warning("No documents to insert")
        except Exception as e:
            db_logger.error(f"Failed to insert documents into MongoDB: {str(e)}")
            raise
    @timing_decorator(db_logger)
    def retrieve(self, query: list[float], k: int = NUMBER_OF_DOCUMENTS_TO_RETRIEVE):
        db_logger.info(f"Querying MongoDB vector index with query of length {len(query)} for top {k} results")
        try:
            pipeline = [
                {
                    "$vectorSearch": {
                        "queryVector": query,
                        "path": self.vector_path,
                        "numCandidates": 300,
                        "limit": int(k),
                        "index": self.index,
                    }
                }
            ]
            results = list(self.collection.aggregate(pipeline))
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
            db_logger.error(f"Vector search query failed: {str(e)}")
            raise

    def close(self):
        db_logger.info("Closing MongoDB connection")
        try:
            self.client.close()
            db_logger.info("MongoDB connection closed successfully")
        except Exception as e:
            db_logger.error(f"Error closing MongoDB connection: {str(e)}")
            raise

