import logging
from flask_cors import CORS
from flask import Flask
from rav_endpoint.main import chat_bp
from rav_endpoint.util import timing_decorator

logger = logging.getLogger(__name__)

@timing_decorator
def register_blueprint(app: Flask):
    """Register the chat blueprint"""
    app.register_blueprint(chat_bp, url_prefix="/api/chat")

def create_app():
    app = Flask(__name__)
    CORS(app)
    register_blueprint(app)

    return app
