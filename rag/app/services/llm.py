from typing import Union
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionUserMessageParam,
    ChatCompletionSystemMessageParam,
)
from rag.app.schemas.data import LLMModel, Document
from rag.app.core.config import settings

key = settings.openai_api_key
client = OpenAI(api_key=key)


def get_llm_response(prompt: str, model: LLMModel = LLMModel.GPT_4):
    try:
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
        used_model = response.model

        result = response.choices[0].message.content
        if not result:
            return "Error: Received null response from OpenAI", None

        metrics = {
            "log_type": "metrics",
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "input_model": model.value,
            "model": used_model,
        }
        return result
    except Exception as e:
        return f"Error: {e}", None


def stream_llm_response(prompt: str, model: str = "gpt-4"):
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


def generate_prompt(
    user_question: str, data: list[Document], max_tokens: int = 1500
) -> str:

    def estimate_tokens(text: str) -> int:
        return len(text) // 4  # Rough approximation

    context_parts = []
    token_count = 0

    for doc in data:
        quote = doc.text.strip()
        metadata_str = ", ".join(f"{k}: {v}" for k, v in doc.metadata.items())

        entry = f'"{quote}"\n(Source: {metadata_str})'
        tokens = estimate_tokens(entry)

        if token_count + tokens > max_tokens:
            break

        context_parts.append(entry)
        token_count += tokens

    context = "\n\n".join(context_parts)

    prompt = """
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
    filled_prompt = prompt.format(
        context=context,
        user_question=user_question,
    )

    return filled_prompt
