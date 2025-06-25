import json
import time
import logging
from shared.util import timing_decorator

logger = logging.getLogger(__name__)



@timing_decorator
def verify(event) -> tuple[bool, str]:
    logger.info("Starting request verification")
    try:
        question = event.get("question")
        if not question:
            logger.warning("Request verification failed: missing question field")
            return False,"body needs to include question"

        logger.info("Request verification successful")
        return True,question

    except json.JSONDecodeError:
        logger.error("Request verification failed: invalid JSON format")
        return False,"body needs to be in json format"
    except ValueError as ve:
        logger.error(f"Request verification failed: ValueError - {ve}")
        return False, str(ve)
    except Exception as e:
        logger.error(f"Request verification failed: unexpected error - {e}")
        return False,str(e)


