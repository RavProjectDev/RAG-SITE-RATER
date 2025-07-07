from pymongo import MongoClient
from typing import cast
import certifi
from shared.classes import Document, VectorEmbedding
from shared.db.connection import Connection

from shared.constants import NUMBER_OF_DOCUMENTS_TO_RETRIEVE, VECTOR_PATH
from shared.logging.utils import timing_context


class MongoConnection(Connection):
    def __init__(self, uri: str, db_name: str, collection_name: str, index: str):
        try:
            self.vector_path = VECTOR_PATH
            self.client = MongoClient(uri, tlsCAFile=certifi.where())
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            self.index = index
        except Exception as e:
            raise

    def insert(self, embedded_data: list[VectorEmbedding]):
        try:
            namespaces_to_insert = list({emb.data.name_space for emb in embedded_data})

            if not namespaces_to_insert:
                return

            existing = self.collection.find(
                {"metadata.name_space": {"$in": namespaces_to_insert}},
                {"metadata.name_space": 1},
            )
            existing_namespaces = {doc["metadata"]["name_space"] for doc in existing}

            # Step 3: Filter out embeddings with already-existing namespaces
            embeddings_to_insert = [
                emb
                for emb in embedded_data
                if emb.data.name_space not in existing_namespaces
            ]

            # Step 4: Insert only the new embeddings
            documents = [emb.to_dict() for emb in embeddings_to_insert]
            if documents:
                self.collection.insert_many(documents)

        except Exception as e:
            raise

    def retrieve(self, query: list[float], k: int = NUMBER_OF_DOCUMENTS_TO_RETRIEVE):
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
            raise

    def close(self):
        try:
            self.client.close()
        except Exception as e:
            raise
