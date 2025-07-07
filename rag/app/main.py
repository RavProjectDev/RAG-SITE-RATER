# main.py

from fastapi import FastAPI
from rag.app.api.v1.endpoints import router as v_1_router
from contextlib import asynccontextmanager

from rag.app.db.connection import Connection
from rag.app.db.mongodb_connection import MongoConnection
from rag.app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_conn: Connection = MongoConnection(
        uri=settings.mongodb_uri,
        db_name=settings.mongodb_db_name,
        collection_name=settings.mongodb_vector_collection,
        index=settings.collection_index,
        vector_path=settings.vector_path,
    )
    app.state.mongo_conn = mongo_conn
    yield
    mongo_conn.close()
app: FastAPI = FastAPI(lifespan=lifespan)

app.include_router(v_1_router, prefix="/api/v1")
