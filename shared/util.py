import functools
import logging
logger = logging.getLogger(__name__)
import time 
def timing_decorator(func):
    """Decorator to log the execution time of functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"[TIMING] {func.__name__} completed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.error(f"[TIMING] {func.__name__} failed after {execution_time:.4f} seconds: {e}")
            raise
    return wrapper