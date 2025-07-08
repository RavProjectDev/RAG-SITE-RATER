# main.py

from fastapi import FastAPI
from rag.app.api.v1.chat import router as chat_router
from rag.app.api.v1.upload import router as upload_router
from rag.app.api.v1.health import router as health_router
from contextlib import asynccontextmanager

from rag.app.db.connection import Connection
from rag.app.db.mongodb_connection import MongoConnection
from rag.app.core.config import settings
from fastapi import Request
import logging
import os

ENV = os.getenv("APP_ENV", "production")


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

app.include_router(chat_router, prefix="/api/v1/chat")
app.include_router(upload_router, prefix="/api/v1/upload")
app.include_router(health_router, prefix="/api/v1/health")
