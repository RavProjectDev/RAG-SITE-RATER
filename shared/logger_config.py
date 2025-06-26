import logging
import os
import sys
import time
import functools
from datetime import datetime
from pathlib import Path

# Create logs directory
logs_dir = Path(__file__).resolve().parent / "logs"
logs_dir.mkdir(exist_ok=True)

def timing_decorator(logger: logging.Logger):
    """Decorator factory that logs execution time with a specific logger"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"[TIMING] {func.__name__} completed in {execution_time:.4f} seconds")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"[TIMING] {func.__name__} failed after {execution_time:.4f} seconds: {e}")
                raise
        return wrapper
    return decorator


def setup_logger(name: str, log_file: Path, level: int) -> logging.Logger:
    """Set up a logger with both file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    return logger

def setup_pipeline_logger() -> logging.Logger:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return setup_logger("embedding_pipeline", logs_dir / f"pipeline_{timestamp}.log", logging.INFO)

def setup_component_logger(component_name: str, level: int = logging.INFO) -> logging.Logger:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return setup_logger(f"embedding_pipeline.{component_name}", logs_dir / f"{component_name}_{timestamp}.log", level)

pipeline_logger = setup_pipeline_logger()
data_logger = setup_component_logger("data")
preprocess_logger = setup_component_logger("preprocess")
embedding_logger = setup_component_logger("embedding")
db_logger = setup_component_logger("database")
llm_logger = setup_component_logger("llm")
legacy_logger = pipeline_logger
