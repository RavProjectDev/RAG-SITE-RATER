import logging
import functools
import time
from contextlib import contextmanager
from shared.logging.classes import AbstractLogger


def timing_decorator(logger: AbstractLogger):
    """Decorator factory that logs execution time with a specific logger"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                raise

        return wrapper

    return decorator


@contextmanager
def timing_context(logger: logging.Logger, name: str):
    start_time = time.time()
    try:
        yield
        elapsed = time.time() - start_time
    except Exception as e:
        elapsed = time.time() - start_time
        raise
