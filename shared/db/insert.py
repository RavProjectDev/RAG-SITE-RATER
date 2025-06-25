from data_embedder.classes import Embedding
from data_embedder.db.connection import Connection
from data_embedder.logger_config import db_logger


def insert_to_db(
    connection: Connection,
    embeddings: list[Embedding],
):
    """
    Inserts a list of embeddings into the database.
    :param connection:
    db connection object that maintains connection to db.
    :param embeddings:
    a list of embeddings to insert into the database.
    :return:
    """
    db_logger.info(f"Starting database insertion of {len(embeddings)} embeddings")
    
    try:
        with connection:
            db_logger.info("Database connection established, inserting embeddings...")
            connection.insert(embeddings)
            db_logger.info(f"Successfully inserted {len(embeddings)} embeddings into database")
    except Exception as e:
        db_logger.error(f"Failed to insert embeddings into database: {str(e)}")
        raise
