from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile
from unittest.mock import patch
from reportlab.pdfgen import canvas
import io
import numpy as np

from accounts.models import User
from organization.models import Organization
from documents.models import Document,DocumentChunk

from documents.tasks import process_document
from documents.embedding import generate_embedding

from documents import views

class DocumentTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.organization=Organization.objects.create(name="yousaf",description="Yousaf company")
        cls.organization2=Organization.objects.create(name="saad",description="Saad company")

        cls.user=User.objects.create_user(username="yousaf123",email="yousaf@gmail.com",password="yousaf123",role=User.Role.ORG_ADMIN,organization=cls.organization)
        cls.user2=User.objects.create_user(username="saad123",email="saad@gmail.com",password="saad123",role=User.Role.ORG_ADMIN,organization=cls.organization2)



        pdf_content=b"fake pdf content here generated"
        buffer = io.BytesIO(pdf_content)    
        cls.pdf1=UploadedFile(name="checking_hr.pdf",file=buffer,content_type="application/pdf")
        cls.pdf2=UploadedFile(name="yousaf_file.pdf",file=buffer,content_type="application/pdf")
        cls.pdf3=UploadedFile(name="saad_file.pdf",file=buffer,content_type="application/pdf")

        cls.document1=Document.objects.create(title="checking_hr",organization=cls.organization,uploaded_by=cls.user,file=cls.pdf1)
        cls.document2=Document.objects.create(title="yousaf_file",organization=cls.organization,uploaded_by=cls.user,file=cls.pdf2)
        cls.document3=Document.objects.create(title="yousaf_file2",organization=cls.organization,uploaded_by=cls.user,file=cls.pdf3)

        newContent=b"my nmae is yousaf"
        buffer1=io.BytesIO(newContent)
        cls.pdf4=UploadedFile(name="saad_file.pdf",file=buffer1,content_type="application/pdf")
        cls.document4=Document.objects.create(title="saad_file",organization=cls.organization2,uploaded_by=cls.user2,file=cls.pdf4)

    # test to get list fo documents
    def test_getdocumentslist(self):


        factory=APIRequestFactory()
        request=factory.get("document/api/v1/documents/")
        force_authenticate(request,user=self.user)

        view=views.DocumentsListView.as_view()
        response=view(request)

        assert response.status_code == 200
        assert isinstance(response.data,list)
        assert len(response.data) == 3
        assert [item["title"] for item in response.data] == ["checking_hr","yousaf_file","yousaf_file2"]


    ## test single document retreivel

    def test_getSingleDocument(self):

        factory=APIRequestFactory()
        request=factory.get(f"document/api/v1/documents/{self.document1.id}/")
        force_authenticate(request,user=self.user)

        view=views.DocumentsRetrieveView.as_view()
        response=view(request, pk=self.document1.id)

        assert response.status_code == 200
        assert response.data["title"] == "checking_hr"


    ## test to send wrong docuemtn id for retreiveal

    def test_getWrongSingleDocument(self):
    
        factory=APIRequestFactory()
        request=factory.get(f"document/api/v1/documents/{5}/")
        force_authenticate(request,user=self.user)

        view=views.DocumentsRetrieveView.as_view()
        response=view(request, pk=5)

        assert response.status_code == 404


    ## test to check multi tenancy
    def test_multitenancyCheck(self):

        factory=APIRequestFactory()
        request=factory.get(f"document/api/v1/documents/{self.document1.id}/")
        force_authenticate(request,user=self.user2)

        view=views.DocumentsRetrieveView.as_view()

        response=view(request,pk=self.document1.id)

        assert response.status_code == 404
        
           
    ## test to check Document Deleteion API
    def test_deleteDocument(self):

        factory=APIRequestFactory()
        request=factory.delete(f'api/v1/documents/delete/{self.document1.id}/')
        force_authenticate(request,user=self.user)
        view=views.DocumentDeleteView.as_view()

        response=view(request,pk=self.document1.id)

        assert response.status_code == 204

    ## test to check Wrong Document Deleteion API
    def test_WrongDeleteDocument(self):

        factory=APIRequestFactory()
        request=factory.delete('api/v1/documents/delete/8/')
        force_authenticate(request,user=self.user)
        view=views.DocumentDeleteView.as_view()

        response=view(request,pk=8)

        assert response.status_code == 404

    ## test to check Wrong Document Deleteion API
    def test_WrongOrganizationDocumentDeletion(self):

        factory=APIRequestFactory()
        request=factory.delete(f'api/v1/documents/delete/{self.document1.id}/')
        force_authenticate(request,user=self.user2)
        view=views.DocumentDeleteView.as_view()

        response=view(request,pk=self.document1.id)

        assert response.status_code == 404

    ## test to check Update Document View API
    def test_DocumentUpdate(self):

        factory=APIRequestFactory()
        data={
            "title":"NEWSaadFile"
        }
        request=factory.patch(f'api/v1/documents/update/{self.document4.id}/',data=data)
        force_authenticate(request,user=self.user2)
        view=views.DocumentUpdateView.as_view()

        response=view(request,pk=self.document4.id)
    

        assert response.data["title"] == "NEWSaadFile"
        assert response.status_code == 200


    ## test to check uploading Document and Chunks Creation using celery task
    def test_DocumentUploadView(self):

        factory=APIRequestFactory() 

        content=b"my name is yousaf i am best developer and this is pdf file for chunks creating and checking docuemnt upload view"

        buffer=io.BytesIO(content)
        pdf_file=UploadedFile(
            name="company_policy.pdf",
            content_type="application/pdf",
            file=buffer
        )

        data={
            "title":"Policies_company_documents",
            "file":pdf_file
        }

        request=factory.post('api/v1/document/upload',data=data,format="multipart")
        view=views.DocumentUploadView.as_view()
        force_authenticate(request,user=self.user2)

        with patch("documents.views.process_document.delay") as mock_test:

            
            response=view(request)
            document=Document.objects.get(title="Policies_company_documents")
            

            assert response.status_code == 201
            assert response.data["title"] == "Policies_company_documents"
            assert document.uploaded_by == self.user2
            assert Document.objects.filter(title="Policies_company_documents").exists()
            mock_test.assert_called_once_with(document.id)


    ## test to check Document Upload view with celery Failed
    def test_DocumentUploadViewCeleryFailed(self):

        factory=APIRequestFactory() 
        
        content=b"my name is yousaf i am best developer and this is pdf file for chunks creating and checking docuemnt upload view"

        buffer=io.BytesIO(content)


        pdf_file=UploadedFile(
            name="company_policy.pdf",
            content_type="application/pdf",
            file=buffer
        )


        data={
            "title":"Policies_company_documents",
            "file":pdf_file
        }

        request=factory.post('api/v1/document/upload',data=data,format="multipart")



        view=views.DocumentUploadView.as_view()
        force_authenticate(request,user=self.user2)

        with patch("documents.views.process_document.delay") as mock_test:

            mock_test.side_effect=ValueError("celery failed")

            response=view(request)

            document=Document.objects.get(title="Policies_company_documents")

            assert Document.objects.filter(title="Policies_company_documents").exists()
            assert document.status == "FAILED"
            mock_test.assert_called_once_with(document.id)
             

    ## test to check Document Processing
    def test_DocumentProcessing(self):

        buffer=io.BytesIO()

        pdf=canvas.Canvas(buffer)

        pdf.drawString(100,750,"we can have 10 days leave adn we can have  vaction package also adn this is document checkr")

        pdf.save()
        buffer.seek(0)

        pdf_file=UploadedFile(
            name="hr_policy.pdf",
            content_type="application/pdf",
            file=buffer
        )

        document=Document.objects.create(title="hr_polict",file=pdf_file,uploaded_by=self.user,organization=self.organization)

        with patch("documents.tasks.generate_embedding") as mock_embdedding:

            mock_embdedding.return_value= np.zeros(384)
            process_document(document.id)
        

            document.refresh_from_db()

            chunks=DocumentChunk.objects.filter(document=document)

            assert DocumentChunk.objects.filter(document=document).exists()
            assert document.status == Document.StatusChoice.READY
            assert chunks.count() == 1

            chunk = DocumentChunk.objects.get(document=document)

            mock_embdedding.assert_called_once()
            assert len(chunk.embedding) == 384



    ## test to check process doucment if document status is already ready before processing document

    def test_ReadyDocumentProcessing(self):
        buffer=io.BytesIO()
        
        pdf=canvas.Canvas(buffer)

        pdf.drawString(100,750,"we can have 10 days leave adn we can have  vaction package also adn this is document checkr")

        pdf.save()
        buffer.seek(0)

        pdf_file=UploadedFile(
            name="hr_policy.pdf",
            content_type="application/pdf",
            file=buffer
        )

        document=Document.objects.create(title="hr_polict",file=pdf_file,uploaded_by=self.user,organization=self.organization)

        document.status=Document.StatusChoice.READY
        document.save(update_fields=["status"])

        with patch("documents.tasks.generate_embedding") as mock_embdedding:

            mock_embdedding.return_value= np.zeros(384)
            process_document(document.id)
            document.refresh_from_db()
            chunks=DocumentChunk.objects.filter(document=document)

            assert document.status == Document.StatusChoice.READY
            assert DocumentChunk.objects.filter(document=document).count() == 0
            mock_embdedding.assert_not_called()


    ## test to check already processing document
    def test_ProcessingDocumentProcessing(self):
        buffer=io.BytesIO()
        
        pdf=canvas.Canvas(buffer)

        pdf.drawString(100,750,"we can have 10 days leave adn we can have  vaction package also adn this is document checkr")

        pdf.save()
        buffer.seek(0)

        pdf_file=UploadedFile(
            name="hr_policy.pdf",
            content_type="application/pdf",
            file=buffer
        )

        document=Document.objects.create(title="hr_polict",file=pdf_file,uploaded_by=self.user,organization=self.organization)

        document.status=Document.StatusChoice.PROCESSING
        document.save(update_fields=["status"])

        with patch("documents.tasks.generate_embedding") as mock_embdedding:

            mock_embdedding.return_value= np.zeros(384)
            process_document(document.id)
            document.refresh_from_db()
            chunks=DocumentChunk.objects.filter(document=document)

            assert document.status == Document.StatusChoice.PROCESSING
            assert DocumentChunk.objects.filter(document=document).count() == 0
            mock_embdedding.assert_not_called()
                
    ## test to check generatge embedding Function
    def test_CheckGenerateEmbedding(self):

        text="my name is yousaf amin khan adn i live in wah cantt and i love tp read book especially about conscious"
        embedding=generate_embedding(text)  
        embedding=embedding.tolist()

        print(embedding)
        print(type(embedding))

        assert len(embedding) == 384
        assert isinstance(embedding,list)


    ## test to check Failed Document 
    def test_FailedDocumentProcessing(self):
        buffer=io.BytesIO()
        
        pdf=canvas.Canvas(buffer)

        pdf.drawString(100,750,"we can have 10 days leave adn we can have  vaction package also adn this is document checkr")

        pdf.save()
        buffer.seek(0)

        pdf_file=UploadedFile(
            name="hr_policy.pdf",
            content_type="application/pdf",
            file=buffer
        )

        document=Document.objects.create(title="hr_policy",file=pdf_file,uploaded_by=self.user,organization=self.organization)

        document.status=Document.StatusChoice.FAILED
        document.save(update_fields=["status"])

        old_chunk = DocumentChunk.objects.create(
        document=document,
        content="OLD CHUNK",
        chunk_index=0,
        embedding=np.zeros(384).tolist()
    )

        # Remember the old chunk's database ID
        old_chunk_id = old_chunk.id

        with patch("documents.tasks.generate_embedding") as mock_embedding:

            mock_embedding.return_value= np.zeros(384)
            process_document(document.id)
            document.refresh_from_db()
            chunks=DocumentChunk.objects.filter(document=document)

            assert document.status == Document.StatusChoice.READY

            # The OLD chunk was deleted
            assert not DocumentChunk.objects.filter(
                id=old_chunk_id
            ).exists()

            # A NEW chunk was created
            assert chunks.count() == 1

            new_chunk = chunks.first()

            # Make sure this is actually new content
            assert "10 days leave" in new_chunk.content

            # Embedding generation happened
            mock_embedding.assert_called_once()

            # New embedding has correct dimensions
            assert len(new_chunk.embedding) == 384
            
            









    
    



