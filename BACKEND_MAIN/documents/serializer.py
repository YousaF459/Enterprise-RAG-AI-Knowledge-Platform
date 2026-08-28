from documents.models import Document
from rest_framework import serializers


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model=Document
        fields=[
            'title',
            'file',
        ]

    def validate_file(self,value):

        if value.content_type != "application/pdf":
            raise serializers.ValidationError(
                "Only PDF files are allowed."
            )

        max_size = 10 * 1024 * 1024  # 10 MB

        if value.size > max_size:
            raise serializers.ValidationError(
            "File size must not exceed 10 MB."
        )

        return value


    def create(self,validated_data):

        user = self.context["request"].user

        validated_data['uploaded_by']=user
        validated_data['organization']=user.organization
        validated_data['status']=Document.StatusChoice.UPLOADING

        return super().create(validated_data)


class QuestionSearchSerializer(serializers.Serializer):
    question=serializers.CharField()


class DocumentsSerializer(serializers.ModelSerializer):

    class Meta:
        model=Document
        fields = [
            "id",
            "organization",
            "uploaded_by",
            "title",
            "file",
            "status",
            "created_at",
            "updated_at",
        ]



class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model=Document
        fields = [
            "id",
            "organization",
            "uploaded_by",
            "title",
            "file",
            "status",
            "created_at",
            "updated_at",
        ]

class DocumentUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ["title"]