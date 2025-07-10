# main.py
import time
import logging

import certifi
from fastapi import FastAPI
from pymongo import MongoClient

from rag.app.api.v1.chat import router as chat_router
from rag.app.api.v1.upload import router as upload_router
from rag.app.api.v1.health import router as health_router
from rag.app.api.v1.mock import router as mock_router
from contextlib import asynccontextmanager

from rag.app.db.connections import EmbeddingConnection
from rag.app.db.mongodb_connection import MongoEmbeddingStore, MongoMetricsConnection

from rag.app.core.config import get_settings, Environment
from rag.app.db.connections import MetricsConnection
from fastapi import Request

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    uri = settings.mongodb_uri
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db = client[settings.mongodb_db_name]
    vector_embedding_collection = db[settings.mongodb_vector_collection]

    mongo_conn: EmbeddingConnection = MongoEmbeddingStore(
        collection=vector_embedding_collection,
        index=settings.collection_index,
        vector_path=settings.vector_path,
    )
    app.state.mongo_conn = mongo_conn

    metrics_collection = db[settings.metrics_collection]

    metrics_connection: MetricsConnection = MongoMetricsConnection(
        collection=metrics_collection,
    )
    app.state.metrics_connection = metrics_connection
    yield
    client.close()


app: FastAPI = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Skip metrics in non-production environments
    settings = get_settings()
    if settings.environment != Environment.PRD:
        return await call_next(request)

    start = time.perf_counter()
    response = await call_next(request)

    if response.status_code not in (200, 500):
        return response

    duration = time.perf_counter() - start
    metrics_connection: MetricsConnection = request.app.state.metrics_connection
    data = {
        "endpoint": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "duration": f"{duration:.4f}",
    }
    metrics_connection.log(
        metric_type="endpoint_timing",
        data=data,
    )
    logger.info(f"{request.method} {request.url.path} completed in {duration:.4f}s")

    return response


app.include_router(chat_router, prefix="/api/v1/chat")
app.include_router(upload_router, prefix="/api/v1/upload")
app.include_router(health_router, prefix="/api/v1/health")
app.include_router(mock_router, prefix="/api/v1/test")
