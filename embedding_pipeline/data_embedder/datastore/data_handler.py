from shared.enums import DataSourceConfiguration
from  embedding_pipeline.data_embedder.datastore.local import get_transcripts_from_local
from shared.logger_config import data_logger


def get_data(configuration: DataSourceConfiguration = DataSourceConfiguration.LOCAL) -> list[tuple[str,str]]:
    """
    Loads transcript data based on the configured data source.

    :param configuration: The source configuration (e.g., LOCAL).
    :return: A list of (filename, file_contents) tuples.
    """
    data_logger.info(f"Loading data with configuration: {configuration.name}")
    data: list[tuple[str, str]] = []
    if configuration.value == DataSourceConfiguration.LOCAL.value:
        data_logger.info("Loading transcripts from local storage...")
        data = get_transcripts_from_local()
        data_logger.info(f"Successfully loaded {len(data)} transcript files from local storage")
    else:
        data_logger.error(f"Unsupported data source configuration: {configuration.name}")
        raise ValueError(f"Unsupported data source configuration: {configuration.name}")

    return data
