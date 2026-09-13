from google import genai
from django.conf import settings
import logging
from documents.exceptions import LLMServiceUnavailable

logger=logging.getLogger(__name__)

client=genai.Client(
    api_key=settings.GEMINI_API_KEY
)

def build_prompt(question,chunks,history):

    context = "\n\n".join(
    f"""
Chunk {chunk.chunk_index}:
{chunk.content}
"""
    for chunk in chunks
)   
    conversation_history=""
    for item in history:
        conversation_history+=f'{item["ROLE"]}:{item["TEXT"]}\n'


    prompt = f"""
You are an AI assistant for an enterprise knowledge platform.

Use ONLY the provided knowledge context to answer the user's question.

If the answer is not contained in the knowledge context, reply exactly:

"I couldn't find that information in the uploaded documents."

Do not use outside knowledge.
Do not make assumptions.

Use ONLY the provided knowledge context to answer the current question.
Conversation history is provided only to understand the context of the conversation.
Do not use information from the conversation history as factual knowledge unless it is supported by the knowledge context.

Conversation history:
{conversation_history}

Knowledge context:
{context}

Current question:
{question}

Answer:
Return only the answer to the user's question.
Do not include sources, document names, chunk numbers, or extra formatting
"""
    return prompt


def generate_answer(question,chunks,history):

    logger.info("Generating answer with Gemini")

    try:

        prompt=build_prompt(question,chunks,history)

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
