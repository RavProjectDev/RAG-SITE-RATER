from typing import Union
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionSystemMessageParam,
)

from flask import current_app

from shared import constants
from shared.enums import LLMModel
from shared.logging.classes import AbstractLogger, LogType
from shared.logging.mongo import MongoLogger
from shared.logging.schemas import LLMCostLog

from shared.logging.utils import timing_context

key = constants.OPENAI_API_KEY
client = OpenAI(api_key=key)


def get_logger() -> AbstractLogger:
    return MongoLogger(
        ds=current_app.config["LOGGING_DATA_SOURCE"], collection_name="llm"
    )


def run_generated_prompt(prompt: str, model: LLMModel = LLMModel.GPT_4) -> str:
    try:
        logger = get_logger()
        messages: list[
            Union[ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam]
        ] = [
            ChatCompletionSystemMessageParam(
                role="system",
                content="You are a helpful assistant knowledgeable in Rav Soloveitchik's teachings.",
            ),
            ChatCompletionUserMessageParam(role="user", content=prompt),
        ]

        response = client.chat.completions.create(
            model=model.value,
            messages=messages,
        )

        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        data = LLMCostLog(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=model,
        )
        logger.log(log_type=LogType.LLM_COST, fields=data)

        result = response.choices[0].message.content
        if not result:
            return "Error: Received null response from OpenAI"

        return result
    except Exception as e:
        return f"Error: {e}"


def stream_llm_response_from_generated_prompt(prompt: str, model: str = "gpt-4"):
    messages: list[
        Union[ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam]
    ] = [
        ChatCompletionSystemMessageParam(
            role="system",
            content="You are a helpful assistant knowledgeable in Rav Soloveitchik's teachings.",
        ),
        ChatCompletionUserMessageParam(role="user", content=prompt),
    ]
    response = client.chat.completions.create(
        model=model, messages=messages, stream=True
    )

    for chunk in response:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield f"{delta.content}"
    yield "data: [DONE]\n\n"
