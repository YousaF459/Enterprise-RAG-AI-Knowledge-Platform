from celery import shared_task
from documents.models import Document,DocumentChunk
from pypdf import PdfReader
from documents.embedding import generate_embedding
from django.db import transaction




@shared_task
def process_document(document_id):

    document=None

    try:

        with transaction.atomic() :

            document=Document.objects.select_for_update().get(id=document_id)

            if document.status==Document.StatusChoice.READY:
                return

            if document.status == Document.StatusChoice.PROCESSING:
                return

            if document.status==Document.StatusChoice.FAILED:
                DocumentChunk.objects.filter(
                    document=document
                ).delete()

            document.status=Document.StatusChoice.PROCESSING
            document.save(update_fields=['status'])

        print(f'Processing : {document.title}')

        text=''

        with document.file.open('rb') as pdf_file:
            reader=PdfReader(pdf_file)

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            raise ValueError("No text could be extracted from the document")        

        chunk_size=1000
        overlap=200
        step=chunk_size - overlap
        chunk_index=0

        for start in range(0,len(text),step):
            end=start + chunk_size
            chunk=text[start:end]

            embedding=generate_embedding(chunk)

            DocumentChunk.objects.create(
                document=document,
                content=chunk,
                chunk_index=chunk_index,
                embedding=embedding.tolist()
            )

            chunk_index+=1


        document.status=Document.StatusChoice.READY
        document.save(update_fields=['status'])

        print(f"{document.title} is READY")

    except Exception as e:

        if document:

            with transaction.atomic():

                document = Document.objects.select_for_update().get(
                    id=document_id
                )

                document.status = Document.StatusChoice.FAILED
                document.save(update_fields=["status"])

        raise