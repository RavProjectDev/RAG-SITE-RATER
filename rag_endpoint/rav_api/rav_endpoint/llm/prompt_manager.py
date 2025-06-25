import logging
from rav_endpoint.classes import Document
from rav_endpoint.util import timing_decorator

logger = logging.getLogger(__name__)

@timing_decorator
def generate_prompt(user_question: str, data: list[Document], max_tokens: int = 1500) -> str:
    logger.info("Starting prompt generation")
    
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

    logger.info(f"Generated prompt with {token_count} estimated tokens from {len(context_parts)} documents")

    return filled_prompt

def generate_using_prompt_id(user_question: str,context: list[Document]) -> dict:
    prompt = { 
        "user_question": user_question,
        "context": "\n".join(document.text for document in context)
    }
    return prompt
