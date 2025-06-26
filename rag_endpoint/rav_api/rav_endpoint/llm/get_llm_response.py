from typing import Union
from openai import OpenAI
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam

from shared.logger_config import timing_decorator,llm_logger
from shared import constants

key = constants.OPENAI_API_KEY
client = OpenAI(api_key=key)

@timing_decorator(llm_logger)
def run_generated_prompt(prompt: str, model: str = "gpt-4") -> str:
    try:
        llm_logger.info("Running OpenAI completion with model: %s", model)
        llm_logger.debug("Prompt: %s", prompt)

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

        llm_logger.info(f"Tokens used — prompt: {prompt_tokens}, completion: {completion_tokens}, total: {total_tokens}")

        result = response.choices[0].message.content 
        if not result:
            return "Error: Received null response from OpenAI"
    
        return result
    except Exception as e:
        llm_logger.error("Error during OpenAI completion: %s", e)
        return f"Error: {e}"

def stream_llm_response_from_generated_prompt(prompt: str, model: str = "gpt-4"):
    messages: list[Union[ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam]] = [
        ChatCompletionSystemMessageParam(role="system",
                                         content="You are a helpful assistant knowledgeable in Rav Soloveitchik's teachings."),
        ChatCompletionUserMessageParam(role="user", content=prompt)
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream = True
    )

    for chunk in response:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield f"{delta.content}"
    yield "data: [DONE]\n\n"


