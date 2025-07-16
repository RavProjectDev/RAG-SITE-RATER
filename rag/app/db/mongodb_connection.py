from typing import cast, Dict, List, Any
import time

from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import OperationFailure

from rag.app.exceptions import EmbeddingError
from rag.app.schemas.data import Document, VectorEmbedding
from rag.app.db.connections import EmbeddingConnection, MetricsConnection
from contextlib import contextmanager
from datetime import datetime


class MongoEmbeddingStore(EmbeddingConnection):
    def __init__(self, collection: AsyncIOMotorCollection, index: str, vector_path: str):
        self.collection = collection
        self.index = index
        self.vector_path = vector_path


    async def insert(self, embedded_data: list[VectorEmbedding]):
        namespaces_to_insert = list({emb.data.name_space for emb in embedded_data})
        if not namespaces_to_insert:
            return

        cursor = self.collection.find(
            {"metadata.name_space": {"$in": namespaces_to_insert}},
            {"metadata.name_space": 1},
        )
        existing = await cursor.to_list(length=None)
        existing_namespaces = {doc["metadata"]["name_space"] for doc in existing}

        embeddings_to_insert = [
            emb for emb in embedded_data if emb.data.name_space not in existing_namespaces
        ]

        documents = [emb.to_dict() for emb in embeddings_to_insert]
        if documents:
            await self.collection.insert_many(documents)

    async def retrieve(self, embedded_data: List[float],name_spaces: list[str] | None = None,k = 5):
        pipeline = []
        if name_spaces is not None:
            pipeline.append({
                "$match": {
                    "metadata.name_space": {"$in": name_spaces}
                }
            })

        pipeline.append({
            "$vectorSearch": {
                "queryVector": embedded_data,
                "path": self.vector_path,
                "numCandidates": 300,
                "limit": int(k),
                "index": self.index,
            }
        })
        try:
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=k)
        except OperationFailure:
            raise EmbeddingError(f"Vector search failed,Dimension of searched vector does not match db vector space dimension "
                                 f"input : {self.vector_path}, vector space: {self.index}")

        documents: list[Document] = []
        for result in results:
            document = Document(
                text=str(result.get("text")),
                vector=cast(list[float], result["vector"]),
                metadata=cast(dict[str, object], result["metadata"]),
            )
            documents.append(document)
        return documents



class MongoMetricsConnection(MetricsConnection):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def log(self, metric_type: str, data: Dict[str, Any]):
        doc = {"type": metric_type, "timestamp": datetime.utcnow(), **data}
        await self.collection.insert_one(doc)

