from google import genai
from django.conf import settings
import logging
from documents.exceptions import LLMServiceUnavailable

logger=logging.getLogger(__name__)

client=genai.Client(
    api_key=settings.GEMINI_API_KEY
)

def build_prompt(question,chunks):

    context = "\n\n".join(
    f"""
Chunk {chunk.chunk_index}:
{chunk.content}
"""
    for chunk in chunks
)


    prompt=f"""
    You are an AI assistant for an enterprise knowledge platform.

Use ONLY the provided context to answer the question.

If the answer is not fully contained in the context, reply exactly:

"I couldn't find that information in the uploaded documents."

Do not use outside knowledge.
Do not make assumptions.

When answering, cite the chunk number(s) you used.

Example:

Employees are entitled to 24 working days of annual leave.

Sources:
- Chunk 35

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    return prompt


def generate_answer(question,chunks):

    logger.info("Generating answer with Gemini")

    try:

        prompt=build_prompt(question,chunks)

        response=client.models.generate_content(
        model= settings.GEMINI_MODEL,
        contents=prompt
        )


        logger.info("Answer Generated succesfully")

        return response.text

    except Exception as e:

        logger.exception("Gemini Request Failed")

        raise LLMServiceUnavailable(
        "LLM service is currently unavailable."
        ) from e
