from django.db import models
from accounts.models import User
from documents.models import DocumentChunk

# Create your models here.
class Conversation(models.Model):
    title=models.CharField(max_length=80)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)




class Message(models.Model):
    conversation=models.ForeignKey(Conversation,on_delete=models.CASCADE)
    text=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    class RoleChoice(models.TextChoices):
        USER= "USER" , "USER"
        ASSISTANT = "ASSISTANT" , "ASSISTANT"

    role=models.CharField(choices=RoleChoice.choices,max_length=15)




class MessageSource(models.Model):
    message=models.ForeignKey(Message,on_delete=models.CASCADE)
    document_chunk = models.ForeignKey(DocumentChunk,on_delete=models.CASCADE)

