from celery import shared_task
from documents.models import Document,DocumentChunk
import time
from pypdf import PdfReader
from documents.embedding import embedding_model,generate_embedding




@shared_task
def process_document(document_id):

    try:
        document=Document.objects.get(id=document_id)
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

        try:
            document.status=Document.StatusChoice.FAILED
            document.save(update_fields=['status'])

        except:
            pass

        raise 