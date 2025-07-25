from typing import Union
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionSystemMessageParam,
)

import asyncio
import logging


from rag.app.db.connections import MetricsConnection
from rag.app.schemas.data import LLMModel
from rag.app.models.data import DocumentModel

from rag.app.exceptions.llm import (
    LLMBaseException,
    LLMTimeoutException,
    LLMConnectionException,
)
from functools import lru_cache
from openai import (
    AsyncOpenAI,
    APIError,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    OpenAIError,
)
from rag.app.core.config import get_settings


@lru_cache()
def get_openai_client() -> AsyncOpenAI:
    try:
        settings = get_settings()
    except (AttributeError, KeyError, TypeError) as e:
        raise LLMBaseException("Failed to get data from settings")
    try:
        return AsyncOpenAI(api_key=settings.openai_api_key)
    except (OpenAIError, AuthenticationError) as e:
        raise LLMConnectionException("OpenAI API connection failed: {}".format(e))


# ---------------------------------------------------------------
# Single-response LLM call
# ---------------------------------------------------------------


async def get_llm_response(
    metrics_connection: MetricsConnection,
    prompt: str,
    model: LLMModel = LLMModel.GPT_4,
) -> str:
    """
    Fetches a synchronous completion from the LLM.
    """
    data = {}
    async with metrics_connection.timed(metric_type="LLM", data=data):
        if model == LLMModel.GPT_4:
            try:
                response, metrics = await get_gpt_response(
                    prompt=prompt, model=model.value
                )
            except Exception as e:
                logging.error(f"Error in get_gpt_response: {e}")
                raise
        elif model == LLMModel.MOCK:
            response, metrics = get_mock_response()
        else:
            raise ValueError(f"Unsupported model: {model}")
        data.update(metrics or {})
        return response


# ---------------------------------------------------------------
# GPT-4 call
# ---------------------------------------------------------------


async def get_gpt_response(
    prompt: str,
    model: str,
) -> tuple[str, dict | None]:

    try:
        client = get_openai_client()
        messages: list[
            Union[ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam]
        ] = [
            ChatCompletionSystemMessageParam(
                role="system",
                content="You are a helpful assistant knowledgeable in Rav Soloveitchik's teachings.",
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=prompt,
            ),
        ]
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
            )
        except OpenAIError as e:
            raise LLMBaseException(f"Failed to get data from OpenAI: {e}")

        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens
        used_model = response.model

        result = response.choices[0].message.content
        if not result:
            return "Error: Received null response from OpenAI", None

        metrics = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "input_model": model,
            "model": used_model,
        }
        return result, metrics

    except Exception as e:
        logging.error(f"Error in get_gpt_response: {e}")
        raise


# ---------------------------------------------------------------
# Mock LLM response
# ---------------------------------------------------------------


def get_mock_response() -> tuple[str, dict]:
    """
    Returns a fixed lorem ipsum mock response and empty metrics.
    """
    return (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
        {},
    )


# ---------------------------------------------------------------
# Streaming LLM call
# ---------------------------------------------------------------


async def stream_llm_response(
    metrics_connection: MetricsConnection,
    prompt: str,
    model: str = "gpt-4",
):
    """
    Streams completion from the LLM as text chunks.
    """
    client = get_openai_client()
    messages = [
        ChatCompletionSystemMessageParam(
            role="system",
            content="You are a helpful assistant knowledgeable in Rav Soloveitchik's teachings.",
        ),
        ChatCompletionUserMessageParam(
            role="user",
            content=prompt,
        ),
    ]
    settings = get_settings()

    try:
        # Make the async streaming API call with timeout
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            ),
            timeout=settings.external_api_timeout,
        )

        async def _consume_stream():
            async for chunk in response:
                print("CHUNK: ", chunk)
                try:
                    if not chunk.choices or not chunk.choices[0].delta:
                        yield "Error: Invalid chunk structure"
                        return
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                except (AttributeError, IndexError):
                    yield "Error: Invalid chunk structure"
                    return
            yield "[DONE]"

        # Stream with metrics and per-token timeout
        async with metrics_connection.timed(metric_type="LLM_STREAM", data={}):
            stream = _consume_stream()
            while True:
                try:
                    token = await asyncio.wait_for(
                        stream.__anext__(), timeout=settings.external_api_timeout
                    )
                    yield token
                except StopAsyncIteration:
                    break

    except asyncio.TimeoutError:
        raise LLMTimeoutException(
            f"LLM call timed out after {settings.external_api_timeout} seconds"
        )
    except AuthenticationError:
        raise LLMConnectionException("Invalid OpenAI API key")
    except RateLimitError:
        raise LLMConnectionException("OpenAI rate limit exceeded")
    except APIConnectionError:
        raise LLMConnectionException("Failed to connect to OpenAI API")
    except APIError as e:
        raise LLMConnectionException(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise LLMBaseException(f"Unexpected error: {str(e)}")


# ---------------------------------------------------------------
# Embedding Generation (incl. mock logic)
# ---------------------------------------------------------------


# ---------------------------------------------------------------
# Prompt Generation
# ---------------------------------------------------------------


def generate_prompt(
    user_question: str,
    data: list[DocumentModel],
    max_tokens: int = 1500,
) -> str:
    """
    Constructs a prompt including retrieved context snippets.
    """

    def estimate_tokens(text: str) -> int:
        return len(text) // 4  # very rough estimate

    context_parts = []
    token_count = 0

    for doc in data:
        quote = doc.text.strip()
        metadata_str = ", ".join(
            f"{k}: {v}" for k, v in doc.metadata.model_dump().items()
        )

        entry = f'"{quote}"\n(Source: {metadata_str})'
        tokens = estimate_tokens(entry)

        if token_count + tokens > max_tokens:
            break

        context_parts.append(entry)
        token_count += tokens

    context = "\n\n".join(context_parts)

    prompt_template = """
        You are a Rav Soloveitchik expert. A user has asked a question about the Rav's philosophy, teachings, or life. Use the quotes and metadata below to construct a thoughtful and accurate response. You must **include the most relevant quotes directly in your answer**, and mention their associated metadata (such as source and page) to support your explanation. If the question is gibberish or unrelated, inquire with the user for clarification.

        # Context
        {context}

        # User Question
        {user_question}

        # Instructions

        1. Understand the Question: Analyze the user’s question to identify the main points of inquiry regarding Rav Soloveitchik.
        2. Review Context: Carefully examine the provided context to locate relevant quotes and metadata that align with the question.
        3. Select Relevant Quotes: Choose the most impactful quotes that directly relate to the user’s question and are supported by the context.
        4. Craft a Response: Construct a clear and comprehensive answer by using the selected quotes. Ensure that you integrate the philosophy and teachings of Rav Soloveitchik into your response.
        5. Include Metadata: For each quote used, include the associated metadata such as the source and page number to substantiate your explanation.
        6. Inquire for Clarity: If the question appears to be gibberish or irrelevant, politely ask the user to clarify or reframe their question to ensure an accurate response.

        # Output Format

        The response should be a well-structured paragraph or multiple paragraphs. 
        - Start with a brief introduction to the topic addressed in the question.
        - Incorporate quotes from Rav Soloveitchik directly into the text, followed by relevant metadata.
        - Conclude with an explanation tying together the quotes and their broader significance to his philosophy, teachings, or life.
    """

    filled_prompt = prompt_template.format(
        context=context,
        user_question=user_question,
    )

    return filled_prompt
