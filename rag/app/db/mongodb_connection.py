from typing import cast, Dict, List, Any
from rag.app.schemas.data import Document, VectorEmbedding
from rag.app.db.embeddingconnection import EmbeddingConnection, MetricsConnection


class MongoEmbeddingStore(EmbeddingConnection):
    def __init__(self, collection, index: str, vector_path: str):
        try:
            self.vector_path = vector_path
            self.collection = collection
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

    def retrieve(self, query: list[float], k: int = 5):
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


from datetime import datetime


class MongoMetricsConnection(MetricsConnection):
    def __init__(self, collection):
        self.collection = collection

    def log(self, metric_type: str, data: Dict[str, Any]):
        doc = {"type": metric_type, "timestamp": datetime.utcnow(), **data}
        self.collection.insert_one(doc)
