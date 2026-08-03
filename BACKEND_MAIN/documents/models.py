from django.db import models
from organization.models import Organization
from accounts.models import User
from pgvector.django import VectorField

# Create your models here.
class Document(models.Model):
    organization=models.ForeignKey(Organization,on_delete=models.CASCADE)
    uploaded_by=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)

    title=models.CharField(max_length=200)

    file=models.FileField(upload_to='documents/')

    created_at=models.DateTimeField(auto_now_add=True)

    updated_at=models.DateTimeField(auto_now=True)

    class StatusChoice(models.TextChoices):
        UPLOADING = "UPLOADING", "UPLOADING"
        PROCESSING = "PROCESSING", "PROCESSING"
        READY = "READY", "READY"
        FAILED = "FAILED", "FAILED"

    status = models.CharField(
    max_length=30,
    choices=StatusChoice.choices,
    default=StatusChoice.UPLOADING,
)



class DocumentChunk(models.Model):

    document=models.ForeignKey(Document,on_delete=models.CASCADE,related_name='chunks')

    content=models.TextField()

    chunk_index=models.IntegerField()

    created_at=models.DateTimeField(auto_now_add=True)

    embedding=VectorField(dimensions=384,null=True,blank=True)

    

    def __str__(self):
        return f'{self.document.title} - chunk {self.chunk_index}'