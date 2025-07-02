from pymongo import MongoClient
from datetime import datetime, timezone
from shared.constants import MONGODB_URI, MONGODB_DB_NAME
from shared.logging.classes import AbstractLogger, LogType
from shared.logging.schemas import Logmodel


class MongoDataSource:
    def __init__(self, mongo_uri, db_name):
        client = MongoClient(mongo_uri)
        self.db = client[db_name]

    def write_log(self, log_data, collection_name):
        collection = self.db[collection_name]
        collection.insert_one(log_data)


class MongoLogger(AbstractLogger):
    def __init__(self, ds, collection_name):
        self.data_source = ds
        self.collection = collection_name

    def log(self, log_type: LogType, fields: Logmodel):
        log_entry = {
            "timestamp": datetime.now(timezone.utc),
            "log_type": log_type.value,
            **fields.model_dump(),
        }
        self.data_source.write_log(log_entry, self.collection)
