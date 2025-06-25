from dotenv import load_dotenv
import os
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "rag_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "transcripts")
MONGO_INDEX = os.getenv("MONGO_COLLECTION","vector_search")
DEFAULT_K = 5
DEFAULT_CHUNK_SIZE = 100 