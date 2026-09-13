##Django Imports
from django.shortcuts import render

## rest framework imports
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

## REST framework VIews
from rest_framework.generics import CreateAPIView,DestroyAPIView,RetrieveDestroyAPIView,ListCreateAPIView

## RESt framework JWT AUTH
from rest_framework_simplejwt.authentication import JWTAuthentication

## Serializers
from conversations import serializer as ConversationSerializers

## MOdels
from accounts.models import User
from documents.models import DocumentChunk
from conversations.models import Conversation,Message,MessageSource

## Swagger
from drf_spectacular.utils import extend_schema,extend_schema_view,OpenApiResponse,OpenApiParameter
from drf_spectacular.types import OpenApiTypes

## Dependency import from documents app
from documents.embedding import generate_embedding
from documents.retreival import retrieve_chunks
from documents.llm import generate_answer


# Seriliazer
from conversations.serializer import QuestionSearchSerializer


## import conversation history
from conversations.conversation_history import history_conversation




####################### Custom Permissionss #######################################

## Creating a Permission for Employee only access 
class isEmployeePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.EMPLOYEE


## Creating a Permission for Employee and admin only access 
class isEmployeeORAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.EMPLOYEE or request.user.role == User.Role.ORG_ADMIN 

#################################### views #####################################################

# class to create a COnversation or get all Conversations
@extend_schema_view(
    post=extend_schema(
        tags=["Conversation"],
        summary="Create a Conversation Container",
        description="Auhtenticated Employee of an organization can Start a chat ",
        request=ConversationSerializers.ConversationSerializer,
        responses=ConversationSerializers.ConversationSerializer
    ),
    get=extend_schema(
        tags=["Conversation"],
        summary="Get all COnversation Container",
        description="An employee can get all his Conversations",
        responses=ConversationSerializers.ConversationSerializer(many=True)
    )
)
class ConversationView(ListCreateAPIView):
    serializer_class=ConversationSerializers.ConversationSerializer
    authentication_classes=[JWTAuthentication]
    permission_classes=[isEmployeePermission,permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)


# Retrieve or Delete a Conversation
@extend_schema_view(
    get=extend_schema(
        summary="Retrieve Conversation",
        description="An employee can retrieve their own conversation.",
        tags=["Conversation"],
        parameters=[
            OpenApiParameter(
                name="pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID of the conversation",
            )
        ],
        responses={
            200: ConversationSerializers.ConversationSerializer,
            401: OpenApiResponse(
                description="Authentication credentials were not provided or are invalid."
            ),
            403: OpenApiResponse(
                description="The authenticated user does not have permission to access this endpoint."
            ),
            404: OpenApiResponse(
                description="Conversation not found."
            ),
        },
    ),

    delete=extend_schema(
        summary="Delete Conversation",
        description="An employee can delete their own conversation.",
        tags=["Conversation"],
        parameters=[
            OpenApiParameter(
                name="pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID of the conversation",
            )
        ],
        responses={
            204: None,
            401: OpenApiResponse(
                description="Authentication credentials were not provided or are invalid."
            ),
            403: OpenApiResponse(
                description="The authenticated user does not have permission to access this endpoint."
            ),
            404: OpenApiResponse(
                description="Conversation not found."
            ),
        },
    ),
)
class ConversationDetailView(RetrieveDestroyAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[isEmployeePermission,permissions.IsAuthenticated]
    serializer_class=ConversationSerializers.ConversationSerializer

    
    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)





## class view for Answer to user question
@extend_schema_view(
    post=extend_schema(
        tags=["Conversation"],
        summary="Send a message to a conversation",
        description=(
            "Accepts a user's question within a conversation, "
            "retrieves relevant document chunks using semantic search, "
            "uses the conversation history and retrieved knowledge "
            "to generate an AI answer, and returns the answer with "
            "its document sources."
        ),
        request=QuestionSearchSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
        },
    )
)
class ConversationMessageCreateView(APIView):

        authentication_classes=[JWTAuthentication]
        permission_classes=[permissions.IsAuthenticated,isEmployeeORAdmin]

        def post(self,request,*args,**kwargs):

            serializer=QuestionSearchSerializer(data=request.data)

            serializer.is_valid(raise_exception=True)

            question=serializer.validated_data['question']


            conversation_id=kwargs["conversation_id"]

            # get conversation
            conversation=Conversation.objects.get(user=request.user,id=conversation_id)


            # get conversation History
            history=history_conversation(conversation)
            
            # save user Message
            user_message=Message.objects.create(
                role=Message.RoleChoice.USER,
                conversation=conversation,
                text=question
            )


            # Generate semantic embedding for the user's question
            question_embedding = generate_embedding(question)
            
            # Retrieve the most relevant document chunks
            query_results=retrieve_chunks(question_embedding,request.user.organization)

            

            

            if not query_results:
                assistant_message=Message.objects.create(
                role=Message.RoleChoice.ASSISTANT,
                conversation=conversation,
                text="I couldn't find that information in the uploaded documents.")

                return Response(
                {
                "question": question,
                "answer": "I couldn't find that information in the uploaded documents.",
                "sources": []
                },
                status=status.HTTP_200_OK
                )

            


            # Generate an answer using the retrieved context
            answer = generate_answer(question, query_results,history)


            # Create assistant MEssage
            assistant_message=Message.objects.create(
                role=Message.RoleChoice.ASSISTANT,
                conversation=conversation,
                text=answer)

            # Create message source for assitatn message
            for items in query_results:
                MessageSource.objects.create(
                    document_chunk=items,
                    message=assistant_message
                )

            sources=[
                {
                    "document":chunk.document.title,
                    "chunk":chunk.chunk_index
                }
                for chunk in query_results
            ]

            return Response({
            "question": question,
            "answer": answer,
            "sources":sources
            },
            status=status.HTTP_200_OK,
            )

    
    


    
    