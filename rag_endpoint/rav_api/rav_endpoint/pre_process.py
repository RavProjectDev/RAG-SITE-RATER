import logging
from rav_endpoint.util import timing_decorator

logger = logging.getLogger(__name__)

QUESTION_WORDS = {"what", "why", "how", "when", "where", "who", "which", "whom", "whose" ,"is" , "the" , "a"}

@timing_decorator
def pre_process(user_query: str) -> str:
    logger.info("Starting pre-processing of user query")
    
    #TODO: Build functions that pre-process the user_query
    user_query = user_query.strip()
    
    user_query = remove_question_words(user_query)
    
    return user_query

def remove_question_words(text: str) -> str:
    words = text.split()
    filtered = [word for word in words if word.lower() not in QUESTION_WORDS]
    result = " ".join(filtered)
    return result

