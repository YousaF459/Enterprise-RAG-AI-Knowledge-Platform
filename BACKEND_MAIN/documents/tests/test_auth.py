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

class TestAuthAndPermissions(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.organization=Organization.objects.create(name="yousaf",description="Yousaf company")
        cls.organization2=Organization.objects.create(name="saad",description="Saad company")

        cls.user=User.objects.create_user(username="yousaf123",email="yousaf@gmail.com",password="yousaf123",role=User.Role.ORG_ADMIN,organization=cls.organization)
        cls.user2=User.objects.create_user(username="saad123",email="saad@gmail.com",password="saad123",role=User.Role.ORG_ADMIN,organization=cls.organization2)
        cls.employee = User.objects.create_user(
    username="employee123",
    email="employee@gmail.com",
    password="employee123",
    role=User.Role.EMPLOYEE,
    organization=cls.organization
        )

        cls.admin = User.objects.create_user(
            username="admin123",
            email="admin@gmail.com",
            password="admin123",
            role=User.Role.SUPER_ADMIN,

        )


        pdf_content=b"fake pdf content here generated"
        buffer = io.BytesIO(pdf_content)    
        cls.pdf1=UploadedFile(name="checking_hr.pdf",file=buffer,content_type="application/pdf")
        cls.pdf2=UploadedFile(name="yousaf_file.pdf",file=buffer,content_type="application/pdf")
        cls.pdf3=UploadedFile(name="saad_file.pdf",file=buffer,content_type="application/pdf")

        cls.document1=Document.objects.create(title="checking_hr",organization=cls.organization,uploaded_by=cls.user,file=cls.pdf1)
        cls.document2=Document.objects.create(title="yousaf_file",organization=cls.organization,uploaded_by=cls.user,file=cls.pdf2)
        cls.document3=Document.objects.create(title="yousaf_file2",organization=cls.organization,uploaded_by=cls.user,file=cls.pdf3)

        newContent=b"my name is yousaf"
        buffer1=io.BytesIO(newContent)
        cls.pdf4=UploadedFile(name="saad_file.pdf",file=buffer1,content_type="application/pdf")
        cls.document4=Document.objects.create(title="saad_file",organization=cls.organization2,uploaded_by=cls.user2,file=cls.pdf4)


    ## checking autheticated User to retrieve document so expected status code 401
    def test_documentRetreiveUnAuthenticated(self):

        factory=APIRequestFactory()
        request=factory.get(f"api/v1/documents/{self.document1.id}/")
        view=views.DocumentsRetrieveView.as_view()

        response=view(request,pk=self.document1.id)

        assert response.status_code == 401

    ##  checking if authenticated employee can retreive document so basiccly checking permission
    def test_documentRetreiveUnauthorized(self):

        factory=APIRequestFactory()
        request=factory.get(f"api/v1/documents/{self.document1.id}/")
        view=views.DocumentsRetrieveView.as_view()
        force_authenticate(request,user=self.employee)
        response=view(request,pk=self.document1.id)

        print(response.data)
        assert response.status_code == 403
        assert response.data["detail"].code == "permission_denied"

    ## test to check if ORG_ADMIN can access documents
    def test_adminRetreiveDocuemnt(self):
        
        factory=APIRequestFactory()
        request=factory.get(f"api/v1/documents/{self.document1.id}/")
        view=views.DocumentsRetrieveView.as_view()
        force_authenticate(request,user=self.admin)
        response=view(request,pk=self.document1.id)

        assert response.status_code == 200
        assert response.data["title"] == "checking_hr"

    ## test to check if one admin can access other organization Resources
    def test_otherOrganizationAdminCannotRetrieveDocument(self):
        
        factory=APIRequestFactory()
        request=factory.get(f"api/v1/documents/{self.document1.id}/")
        view=views.DocumentsRetrieveView.as_view()
        force_authenticate(request,user=self.user2)
        response=view(request,pk=self.document1.id)

        assert response.status_code == 404

    ## TEST to check if admin of one organization can delete resources of other organization
    def test_checkDeletedoucment(self):

        factory=APIRequestFactory()
        request=factory.delete(f"api/v1/documents/delete/{self.document1.id}/")
        view=views.DocumentDeleteView.as_view()
        force_authenticate(request,user=self.user2)
        response=view(request,pk=self.document1.id)

        print(response.data)
        assert response.status_code == 404
        assert Document.objects.filter(id=self.document1.id).exists()

