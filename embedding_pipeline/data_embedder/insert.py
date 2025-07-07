import argparse
import os

from shared.db.mongodb_connection import MongoConnection
from shared.db.connection import Connection
from shared.enums import DataSourceConfiguration, TypeOfFormat, EmbeddingConfiguration
from embedding_pipeline.data_embedder.datastore.data_handler import get_data
from preprocess.preprocess_raw_transcripts import run as preprocess_raw_transcripts
from shared.classes import Chunk, VectorEmbedding
from shared import constants
from embedding_pipeline.data_embedder.embed_util import embedding_helper
from logging import getLogger

logger = getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Populate vector DB with embedded RAV transcripts."
    )

    parser.add_argument(
        "--source",
        choices=[e.name for e in DataSourceConfiguration],
        default="LOCAL",
        help="Data source location",
    )
    parser.add_argument(
        "--db",
        choices=[e.name for e in DataSourceConfiguration],
        default="MONGO",
        help="Vector DB to use",
    )
    parser.add_argument(
        "--embedder",
        choices=[e.name for e in EmbeddingConfiguration],
        default="BERT_SMALL_TRANSLATED",
        help="Embedding model to use",
    )
    parser.add_argument(
        "--format",
        choices=[e.name for e in TypeOfFormat],
        default="SRT",
        help="Transcript format (SRT or TXT)",
    )

    return parser.parse_args()


def main(
    connection: Connection,
    data_source_config: DataSourceConfiguration,
    embedding_configuration: EmbeddingConfiguration,
    data_format: TypeOfFormat,
):

    logger.info(
        f"Starting embedding pipeline with config: source={data_source_config.name}, embedder={embedding_configuration.name}, format={data_format.name}"
    )
    logger.info("Loading raw transcripts...")
    raw_transcripts = get_data(configuration=data_source_config)
    logger.info(f"Loaded {len(raw_transcripts)} raw transcript files")

    logger.info("Preprocessing transcripts...")
    processed_transcripts: list[Chunk] = preprocess_raw_transcripts(
        raw_transcripts=raw_transcripts, data_format=data_format
    )

    logger.info(f"Preprocessed {len(processed_transcripts)} chunks")
    logger.info("Generating embeddings...")

    embedded_transcripts: list[VectorEmbedding] = embedding_helper(
        chunks=processed_transcripts, configuration=embedding_configuration
    )
    logger.info(f"Generated {len(embedded_transcripts)} embeddings")

    logger.info("Inserting embeddings into database...")
    connection.insert(embedded_transcripts)
    logger.info("Successfully completed embedding pipeline")
    logger.info("Evaluating embedding accuracy...")


if __name__ == "__main__":
    logger.info("Initializing embedding pipeline...")
    args = parse_args()
    logger.info(f"Command line arguments: {vars(args)}")

    if args.source == "LOCAL":
        data_source_config = DataSourceConfiguration.LOCAL
        logger.info("Using LOCAL data source configuration")
    else:
        logger.error(f"Unsupported data source: {args.source}")
        raise ValueError(f"Unsupported data source: {args.source}")

    connection: Connection
    if args.db == "MONGO":
        logger.info("Setting up MongoDB connection...")
        mongo_uri = constants.MONGODB_URI
        mongo_db = constants.MONGODB_DB_NAME
        mongo_collection = constants.MONGODB_VECTOR_COLLECTION
        index = constants.COLLECTION_INDEX
        if not mongo_uri or not mongo_db or not mongo_collection:
            logger.error("Missing required MongoDB environment variables")
            raise ValueError(
                "Missing required MongoDB environment variables: MONGO_URI, MONGO_DATABASE, MONGO_COLLECTION"
            )
        connection = MongoConnection(
            index=index,
            uri=mongo_uri,
            db_name=mongo_db,
            collection_name=mongo_collection,
        )
        logger.info("MongoDB connection configured")
    else:
        logger.error(f"Unsupported vector DB: {args.db}")
        raise ValueError(f"Unsupported vector DB: {args.db}")

    if args.embedder == "BERT_SMALL_TRANSLATED":
        embedding_configuration = EmbeddingConfiguration.BERT_SMALL_TRANSLATED
        logger.info("Using BERT_SMALL_TRANSLATED embedding configuration")
    elif args.embedder == "BART_SMALL":
        embedding_configuration = EmbeddingConfiguration.BERT_SMALL
        logger.info("Using BERT_SMALL embedding configuration")
    elif args.embedder == "GEMINI":
        embedding_configuration = EmbeddingConfiguration.GEMINI
    else:
        logger.error(f"Unsupported embedder: {args.embedder}")
        raise ValueError(f"Unsupported embedder: {args.embedder}")

    if args.format == "SRT":
        data_format = TypeOfFormat.SRT
        logger.info("Using SRT format for transcripts")
    elif args.format == "TXT":
        data_format = TypeOfFormat.TXT
        logger.info("Using TXT format for transcripts")
    else:
        logger.error(f"Unsupported format: {args.format}")
        raise ValueError(f"Unsupported format: {args.format}")

    try:
        main(
            connection=connection,
            data_source_config=data_source_config,
            embedding_configuration=embedding_configuration,
            data_format=data_format,
        )
        logger.info("Pipeline completed successfully")
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
        raise
