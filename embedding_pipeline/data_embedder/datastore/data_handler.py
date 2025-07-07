from shared.enums import DataSourceConfiguration
from  embedding_pipeline.data_embedder.datastore.local import get_transcripts_from_local
from logging import getLogger
logger = getLogger(__name__)

def get_data(configuration: DataSourceConfiguration = DataSourceConfiguration.LOCAL) -> list[tuple[str,str]]:
    """
    Loads transcript data based on the configured data source.

    :param configuration: The source configuration (e.g., LOCAL).
    :return: A list of (filename, file_contents) tuples.
    """
    logger.info(f"Loading data with configuration: {configuration.name}")
    if configuration.value == DataSourceConfiguration.LOCAL.value:
        logger.info("Loading transcripts from local storage...")
        data = get_transcripts_from_local()
        logger.info(f"Successfully loaded {len(data)} transcript files from local storage")
    else:
        logger.error(f"Unsupported data source configuration: {configuration.name}")
        raise ValueError(f"Unsupported data source configuration: {configuration.name}")

    return data
