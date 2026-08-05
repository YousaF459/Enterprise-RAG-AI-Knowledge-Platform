from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from documents.exceptions import (LLMServiceUnavailable,EmbeddingGenerationError,RetrievalError)

def custom_exception_handler(exc,context):

    response=exception_handler(exc,context)

    if response is not None:
        return response


    if isinstance(exc,LLMServiceUnavailable):

        return Response(
            {
            "error": "AI service is temporarily unavailable. Please try again later."
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    if isinstance(exc,RetrievalError):
        return Response({
            "error":"Unable to search the knowledge base at the moment. Please try again later"
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    if isinstance(exc,EmbeddingGenerationError):
        return Response(
            {
            "error": "Unable to process your question at the moment. Please try again later"
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


    return Response(
        {
            "error":"Something went wrong. Please try again later."
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )