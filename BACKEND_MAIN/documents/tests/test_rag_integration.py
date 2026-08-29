from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from django.test import TestCase
from django.core.files.uploadedfile import UploadedFile
from unittest.mock import patch
from reportlab.pdfgen import canvas
import io
import numpy as np
from pathlib import Path
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import User
from organization.models import Organization
from documents.models import Document,DocumentChunk

from documents.tasks import process_document
from documents.embedding import generate_embedding

from documents import views



class RAGTesting(TestCase):

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

    # test to cehck QUestion Search view for chunks retreivel based on question
    def test_QuestionSearchView(self):
    
        factory=APIRequestFactory()
        data={
            "question":"what is company leave policy?"
        }
        request=factory.post("document/api/v1/question/search",data=data)
        view=views.QuestionSearchView.as_view()

        pdf_path=Path(__file__).parent / 'fixtures' / 'hr_policy.pdf'

        with open(pdf_path,"rb") as f:

            pdf_file=SimpleUploadedFile(
                name="hr_policy.pdf",
                content_type="application/pdf",
                content=f.read()
            )

        document=Document.objects.create(organization=self.organization,uploaded_by=self.user,title="hr_policy",file=pdf_file)
        process_document(document.id)

        document.refresh_from_db()

        force_authenticate(request,user=self.user)

        response=view(request)


        assert document.status == Document.StatusChoice.READY
        assert DocumentChunk.objects.filter(document=document).count() != 0
        chunks = DocumentChunk.objects.filter(document=document)

        assert chunks.exists()
        assert response.data["question"] == "what is company leave policy?"
        assert len(response.data["sources"]) > 0