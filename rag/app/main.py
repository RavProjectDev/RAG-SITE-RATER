import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from fastapi.middleware.cors import CORSMiddleware


from rag.app.api.v1.chat import router as chat_router
from rag.app.api.v1.data_management import router as upload_router
from rag.app.api.v1.health import router as health_router
from rag.app.api.v1.docs import router as docs_router
from rag.app.api.v1.mock import router as mock_router
from rag.app.api.v1.form import router as form_router
from rag.app.db.connections import MetricsConnection, ExceptionsLogger

from rag.app.db.mongodb_connection import (
    MongoEmbeddingStore,
    MongoMetricsConnection,
    MongoExceptionsLogger,
)
from rag.app.core.config import get_settings, Environment
from rag.app.core.scheduler import start_scheduler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    client = AsyncIOMotorClient(
        settings.mongodb_uri, tlsCAFile=certifi.where(), maxPoolSize=50
    )
    try:
        db = client[settings.mongodb_db_name]
        vector_embedding_collection = db[settings.mongodb_vector_collection]
        metrics_collection = db[settings.metrics_collection]
        exceptions_collection = db[settings.exceptions_collection]

        mongo_connection = MongoEmbeddingStore(
            collection=vector_embedding_collection,
            index=settings.collection_index,
            vector_path=settings.vector_path,
        )
        metrics_connection = MongoMetricsConnection(
            collection=metrics_collection,
        )
        exceptions_logger = MongoExceptionsLogger(
            collection=exceptions_collection,
        )

        app.state.mongo_conn = mongo_connection
        app.state.metrics_connection = metrics_connection
        app.state.exceptions_logger = exceptions_logger
        app.state.db_client = db
        start_scheduler(
            connection=mongo_connection,
            embedding_configuration=settings.embedding_configuration,
        )
        yield

    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        raise
    finally:
        client.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    settings = get_settings()
    if settings.environment != Environment.PRD:
        return await call_next(request)

    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    data = {
        "endpoint": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "duration": duration,  # Store as float
    }
    if response.status_code == 200:
        metrics_connection: MetricsConnection = request.app.state.metrics_connection
        await metrics_connection.log(metric_type="endpoint_timing", data=data)
    else:
        exceptions_logger: ExceptionsLogger = request.app.state.exceptions_logger
        await exceptions_logger.log(
            exception_code=None,
            data=data,
        )
        logger.info(f"{request.method} {request.url.path} completed in {duration:.4f}s")
    logger.info(f"{request.method} {request.url.path} completed in {duration:.4f}s")
    return response


app.include_router(chat_router, prefix="/api/v1/chat")
app.include_router(upload_router, prefix="/api/v1/upload")
app.include_router(health_router, prefix="/api/v1/health")
app.include_router(mock_router, prefix="/api/v1/test")
app.include_router(docs_router, prefix="")

app.include_router(form_router, prefix="/form")
