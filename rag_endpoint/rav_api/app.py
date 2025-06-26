from flask_cors import CORS
from flask import Flask
from rag_endpoint.rav_api.rav_endpoint.main import chat_bp


def register_blueprint(app: Flask):
    """Register the chat blueprint"""
    app.register_blueprint(chat_bp, url_prefix="/api/chat")

def create_app():
    app = Flask(__name__)
    CORS(app)
    register_blueprint(app)

    return app
app= create_app()
