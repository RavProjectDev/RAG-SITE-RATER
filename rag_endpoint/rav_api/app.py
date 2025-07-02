from flask_cors import CORS
from flask import Flask
from rag_endpoint.rav_api.rav_endpoint.main import chat_bp
from shared.logging.classes import AbstractLogger
from shared.logging.mongo import MongoDataSource, MongoLogger
from shared.db.mongodb_connection import MongoConnection, Connection
from shared.enums import EmbeddingConfiguration

from shared.constants import (
    MONGODB_URI,
    MONGODB_DB_NAME,
    MONGODB_VECTOR_COLLECTION,
    COLLECTION_INDEX,
)


assert MONGODB_URI is not None, "MONGODB_URI environment variable is not set"
assert MONGODB_DB_NAME is not None, "MONGODB_DB_NAME environment variable is not set"
assert (
    MONGODB_VECTOR_COLLECTION is not None
), "MONGODB_VECTOR_COLLECTION environment variable is not set"
assert COLLECTION_INDEX is not None, "COLLECTION_INDEX environment variable is not set"


def register_blueprint(app: Flask):
    """Register the chat blueprint"""
    app.register_blueprint(chat_bp, url_prefix="/api/chat")


def create_app():
    app = Flask(__name__)
    mongo_ds = MongoDataSource(mongo_uri=MONGODB_URI, db_name=MONGODB_DB_NAME)
    app.config["DATA_SOURCE"] = mongo_ds
    embedding_configuration = EmbeddingConfiguration.GEMINI
    app.config["EMBEDDING_CONFIGURATION"] = embedding_configuration
    connection: Connection = MongoConnection(
        uri=MONGODB_URI,
        collection_name=MONGODB_VECTOR_COLLECTION,
        index=COLLECTION_INDEX,
        db_name=MONGODB_DB_NAME,
    )
    app.config["CONNECTION"] = connection
    mongo_ds = MongoDataSource(
        mongo_uri=MONGODB_URI,
        db_name=MONGODB_DB_NAME,
    )
    app.config["LOGGING_DATA_SOURCE"] = mongo_ds
    CORS(app)
    register_blueprint(app)
    return app


app = create_app()
