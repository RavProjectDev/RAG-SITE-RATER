from shared.classes import VectorEmbedding
from rag.app.db.connections import EmbeddingConnection
from logging import getLogger

logger = getLogger(__name__)


def insert_to_db(
    connection: EmbeddingConnection,
    embeddings: list[VectorEmbedding],
):
    """
    Inserts a list of embeddings into the database.
    :param connection:
    db connection object that maintains connection to db.
    :param embeddings:
    a list of embeddings to insert into the database.
    :return:
    """
    logger.info(f"Starting database insertion of {len(embeddings)} embeddings")

    try:
        with connection:
            logger.info("Database connection established, inserting embeddings...")
            connection.insert(embeddings)
            logger.info(
                f"Successfully inserted {len(embeddings)} embeddings into database"
            )
    except Exception as e:
        logger.error(f"Failed to insert embeddings into database: {str(e)}")
        raise
