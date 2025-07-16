import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import certifi

from rag.app.api.v1.chat import router as chat_router
from rag.app.api.v1.upload import router as upload_router
from rag.app.api.v1.health import router as health_router
from rag.app.api.v1.mock import router as mock_router
from rag.app.db.connections import EmbeddingConnection, MetricsConnection
from rag.app.db.mongodb_connection import MongoEmbeddingStore, MongoMetricsConnection
from rag.app.core.config import get_settings, Environment

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    try:
        client = AsyncIOMotorClient(settings.mongodb_uri, tlsCAFile=certifi.where(), maxPoolSize=50)
        db = client[settings.mongodb_db_name]
        vector_embedding_collection = db[settings.mongodb_vector_collection]
        metrics_collection = db[settings.metrics_collection]

        app.state.mongo_conn = MongoEmbeddingStore(
            collection=vector_embedding_collection,
            index=settings.collection_index,
            vector_path=settings.vector_path,
        )
        app.state.metrics_connection = MongoMetricsConnection(
            collection=metrics_collection,
        )
        yield
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        raise
    finally:
        client.close()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    settings = get_settings()
    if settings.environment != Environment.PRD:
        return await call_next(request)

    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    if response.status_code in (200, 500) and hasattr(request.app.state, 'metrics_connection'):
        metrics_connection: MetricsConnection = request.app.state.metrics_connection
        data = {
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration": duration,  # Store as float
        }
        metrics_connection.log(metric_type="endpoint_timing", data=data)
    logger.info(f"{request.method} {request.url.path} completed in {duration:.4f}s")
    return response

app.include_router(chat_router, prefix="/api/v1/chat")
app.include_router(upload_router, prefix="/api/v1/upload")
app.include_router(health_router, prefix="/api/v1/health")
app.include_router(mock_router, prefix="/api/v1/test")