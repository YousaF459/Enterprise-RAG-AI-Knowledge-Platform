from conversations.models import Conversation,Message,MessageSource
from rest_framework.serializers import Serializer,ModelSerializer
from rest_framework import serializers

class ConversationSerializer(ModelSerializer):

    class Meta:
        model=Conversation
        fields=[
            "id",
            "title",
            "created_at",
            "updated_at"
        ]
        read_only_fields=[
            "created_at",
            "updated_at"       
        ]



class MessageSerializer(ModelSerializer):

    class Meta:
        model=Message
        fields=[
            "text"
        ]
        


class QuestionSearchSerializer(serializers.Serializer):
    question=serializers.CharField()


