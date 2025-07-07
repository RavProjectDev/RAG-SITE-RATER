import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", log_format: Optional[str] = None) -> None:
    """
    Setup logging configuration for the RAV application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string. If None, uses default format.
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("rav_application.log"),
        ],
    )

    # Set specific logger levels
    loggers = [
        "rav_api.rav_endpoint",
        "rav_api.rav_endpoint.main",
        "rav_api.rav_endpoint.embedding",
        "rav_api.rav_endpoint.vector_db",
        "rav_api.rav_endpoint.llm",
        "rav_api.rav_endpoint.pre_process",
        "rav_api.rav_endpoint.util",
        "app",
        "__main__",
    ]

    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper()))

    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def get_timing_logger(name: str) -> logging.Logger:
    """
    Get a logger specifically for timing information.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"{name}.timing")


def log_timing(
    logger: logging.Logger,
    operation: str,
    duration: float,
    request_id: Optional[str] = None,
    additional_info: Optional[str] = None,
) -> None:
    """
    Log timing information in a consistent format.

    Args:
        logger: Logger instance
        operation: Name of the operation being timed
        duration: Duration in seconds
        request_id: Optional request ID for correlation
        additional_info: Optional additional information to log
    """
    request_prefix = f"[{request_id}] " if request_id else ""
    info_suffix = f" - {additional_info}" if additional_info else ""

    logger.info(
        f"{request_prefix}[TIMING] {operation} completed in {duration:.4f} seconds{info_suffix}"
    )
