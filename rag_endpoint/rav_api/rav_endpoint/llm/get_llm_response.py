from typing import Union
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam
import os
from dotenv import load_dotenv
load_dotenv()
import logging

from shared.util import timing_decorator

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=key)
@timing_decorator
def run_generated_prompt(prompt: str, model: str = "gpt-4") -> str:
    try:
        logger.info("Running OpenAI completion with model: %s", model)
        logger.debug("Prompt: %s", prompt)

        messages: list[Union[ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam]] = [
            ChatCompletionSystemMessageParam(role="system", content="You are a helpful assistant knowledgeable in Rav Soloveitchik's teachings."),
            ChatCompletionUserMessageParam(role="user", content=prompt)
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )

        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        logger.info(f"Tokens used — prompt: {prompt_tokens}, completion: {completion_tokens}, total: {total_tokens}")

        result = response.choices[0].message.content 
        if not result:
            return "Error: Received null response from OpenAI"
    
        return result
    except Exception as e:
        logger.error("Error during OpenAI completion: %s", e)
        return f"Error: {e}"

