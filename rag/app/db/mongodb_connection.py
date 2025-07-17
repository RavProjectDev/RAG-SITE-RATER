from typing import cast, Dict, List, Any

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import OperationFailure, ExecutionTimeout

from rag.app.exceptions.db import (
    RetrievalException,
    DataBaseException,
    InsertException,
    RetrievalTimeoutException,
    NoDocumentFoundException,
)
from rag.app.schemas.data import Document, VectorEmbedding
from rag.app.db.connections import EmbeddingConnection, MetricsConnection
from datetime import datetime


class MongoEmbeddingStore(EmbeddingConnection):
    def __init__(
        self, collection: AsyncIOMotorCollection, index: str, vector_path: str
    ):
        self.collection = collection
        self.index = index
        self.vector_path = vector_path

    async def insert(self, embedded_data: list[VectorEmbedding]):
        namespaces_to_insert = list({emb.data.name_space for emb in embedded_data})
        if not namespaces_to_insert:
            return
        try:
            cursor = self.collection.find(
                {"metadata.name_space": {"$in": namespaces_to_insert}},
                {"metadata.name_space": 1},
            )
            existing = await cursor.to_list(length=None)
            existing_namespaces = {doc["metadata"]["name_space"] for doc in existing}

            embeddings_to_insert = [
                emb
                for emb in embedded_data
                if emb.data.name_space not in existing_namespaces
            ]

            documents = [emb.to_dict() for emb in embeddings_to_insert]
            if documents:
                await self.collection.insert_many(documents)
        except OperationFailure as e:
            raise InsertException(
                f"Failed to insert documents, Mongo config error: {e}"
            )
        except Exception as e:
            raise DataBaseException(f"Failed to insert documents: {e}")

    async def retrieve(
        self,
        embedded_data: List[float],
        name_spaces: list[str] | None = None,
        k=5,
        THRESHOLD: int = 0.85,
    ):
        pipeline = []
        if name_spaces is not None and len(name_spaces) > 0:
            print("HERE")
            pipeline.append({"$match": {"metadata.name_space": {"$in": name_spaces}}})
        pipeline.append(
            {
                "$vectorSearch": {
                    "index": self.index,
                    "path": self.vector_path,
                    "queryVector": embedded_data,
                    "numCandidates": 300,
                    "limit": int(k),
                    "metric": "cosine",  # add if needed
                }
            }
        )

        # Add the similarity score as a field named "score"
        pipeline.append({"$addFields": {"score": {"$meta": "vectorSearchScore"}}})

        # Filter documents with score >= THRESHOLD
        pipeline.append({"$match": {"score": {"$gte": THRESHOLD}}})

        # Optionally exclude the vector field from the results
        pipeline.append(
            {
                "$project": {
                    "text": 1,
                    "metadata": 1,
                    "score": 1,
                }
            }
        )
        try:
            cursor = self.collection.aggregate(pipeline, maxTimeMS=500)
            results = await cursor.to_list(length=k)

        except ExecutionTimeout as e:
            raise RetrievalTimeoutException(
                f"Failed to retrieve documents. Request timed out: {e}"
            )
        except OperationFailure as e:
            raise RetrievalException("Mongo failed to retrieve documents: {}".format(e))
        except Exception as e:
            raise DataBaseException(f"Failed to retrieve documents: {e}")

        documents: list[Document] = []
        for result in results:
            metadata = cast(dict[str, object], result["metadata"])
            metadata["score"] = result["score"]
            document = Document(
                text=str(result.get("text")),
                metadata=metadata,
            )
            documents.append(document)
        if len(documents) == 0:
            raise NoDocumentFoundException
        return documents


class MongoMetricsConnection(MetricsConnection):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def log(self, metric_type: str, data: Dict[str, Any]):
        doc = {"type": metric_type, "timestamp": datetime.utcnow(), **data}
        await self.collection.insert_one(doc)
