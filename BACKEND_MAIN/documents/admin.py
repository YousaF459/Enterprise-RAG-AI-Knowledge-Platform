from django.contrib import admin
from documents.models import Document,DocumentChunk
# Register your models here.

admin.site.register(Document)


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "document",
        "chunk_index",
        "created_at",
    ]