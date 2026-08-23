from django.shortcuts import render
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView
from rest_framework.permissions import BasePermission
from accounts.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import documents.serializer as document_serializers
from .tasks import process_document
from drf_spectacular.utils import extend_schema_view,extend_schema,OpenApiResponse
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.types import OpenApiTypes
from documents.models import DocumentChunk
from pgvector.django import CosineDistance
from documents.retreival import retrieve_chunks
from documents.llm import generate_answer
from .exceptions import LLMServiceUnavailable,EmbeddingGenerationError,RetrievalError
from .models import Document
from documents.embedding import generate_embedding
# Create your views here.

## allow permission for ORG_ADMIn

class IsOrgAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == User.Role.ORG_ADMIN

## allow permmission for EMployee or org_admin
class IsEmployeeOrOrgADmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == User.Role.EMPLOYEE or request.user.role==User.Role.ORG_ADMIN

## allow permission for Employee or Superadmin
class IsSuperAdminOrOrgADmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == User.Role.SUPER_ADMIN or request.user.role==User.Role.ORG_ADMIN




## class view for document uploading handling
@extend_schema_view(
    post=extend_schema(
        tags=["Documents"],
        summary="Upload Document",
        description=(
            "Upload a document for the authenticated organization. "
            "The document is saved to the database and a Celery background "
            "task is queued to process the document asynchronously."
        ),
        request={
            'multipart/form-data': document_serializers.DocumentUploadSerializer
        },
        responses={
            201: document_serializers.DocumentUploadSerializer,
            400: None,
            401: None,
            403: None,
        },
    )
)
class DocumentUploadView(CreateAPIView):

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsOrgAdmin]
    serializer_class=document_serializers.DocumentUploadSerializer
    parser_classes=[MultiPartParser,FormParser]

        

    def perform_create(self, serializer):

        document = serializer.save()

        process_document.delay(document.id)

## class view for user Questions adn search database for chunks

@extend_schema_view(
    post=extend_schema(
        tags=['Documents'],
        summary="Semantic Search",
        description=(
            "Accepts a user's question, generates an embedding, "
            "performs semantic search over document chunks, "
            "and returns the most relevant results."
        ),
        request=document_serializers.QuestionSearchSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
        },
    )
)
class QuestionSearchView(APIView):

        authentication_classes=[JWTAuthentication]
        permission_classes=[IsAuthenticated,IsEmployeeOrOrgADmin]

        def post(self,request,*args,**kwargs):

            serializer=document_serializers.QuestionSearchSerializer(data=request.data)

            serializer.is_valid(raise_exception=True)

            question=serializer.validated_data['question']


            # Generate semantic embedding for the user's question
            question_embedding = generate_embedding(question)
            
            # Retrieve the most relevant document chunks
            query_results=retrieve_chunks(question_embedding,request.user.organization)
            

            if not query_results:
                return Response(
                {
                "question": question,
                "answer": "I couldn't find that information in the uploaded documents.",
                "sources": []
                },
                status=status.HTTP_200_OK
                )

            # Generate an answer using the retrieved context
            answer = generate_answer(question, query_results)

            sources=[
                {
                    "document":chunk.document.title,
                    "chunk":chunk.chunk_index
                }
                for chunk in query_results
            ]

            return Response(
            {
            "question": question,
            "answer": answer,
            "sources":sources
            },
            status=status.HTTP_200_OK,
            )


## class to get documents related to user organization
@extend_schema_view(
    get=extend_schema(
        tags=["Documents"],
        summary="Retreive Organization Documents",
        description=(
            "Retrieve documents available to the authenticated administrator. "
            "SUPER_ADMIN users can retrieve documents from all organizations, "
            "while ORG_ADMIN users can retrieve documents belonging only to "
            "their own organization."
        ),
        responses=document_serializers.DocumentsSerializer(many=True),
    )
)
class DocumentsListView(ListAPIView):

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsSuperAdminOrOrgADmin]
    serializer_class=document_serializers.DocumentsSerializer

    def get_queryset(self):

        user=self.request.user
        organization=user.organization

        if user.role == User.Role.SUPER_ADMIN:
            return Document.objects.all()
        
        return Document.objects.filter(organization=organization)


## class to retreive A specific Document

@extend_schema_view(
    get=extend_schema(
        tags=["Documents"],
        summary="Retrieve Document Details",
        description=(
            "Retrieve the details of a specific document. "
            "SUPER_ADMIN users can retrieve documents from any organization, "
            "while ORG_ADMIN users can retrieve documents belonging only to "
            "their own organization."
        ),
        responses=document_serializers.DocumentSerializer,
    )
)
class DocumentsRetreiveView(RetrieveAPIView):

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsSuperAdminOrOrgADmin]
    serializer_class=document_serializers.DocumentSerializer


    def get_queryset(self):

        user = self.request.user

        if user.role == User.Role.SUPER_ADMIN:
            return Document.objects.all()

        return Document.objects.filter(
            organization=user.organization
        )
        