from django.test import TestCase
from rest_framework.test import APIRequestFactory,force_authenticate
from django.core.files.uploadedfile import SimpleUploadedFile,UploadedFile
import io
from unittest.mock import patch

from organization.models import Organization
from accounts.models import User
from documents.models import Document

from documents import views as DocumentViews

from documents.tasks import process_document

class ValidationTesting(TestCase):

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



    def test_DocumentUploadView_test_upload_empty_title(self):

        factory=APIRequestFactory()

        pdf_cotent=b"we are checking if title is empty waht will happen"
        buffer=io.BytesIO(pdf_cotent)

        pdf_file=UploadedFile(
            name="checking_hr.pdf",
            content_type="application/pdf",
            file=buffer
        )

        data={
            "title":"",
            "file":pdf_file
        }
        request=factory.post("api/v1/document/upload",data=data,format="multipart")
        force_authenticate(request,user=self.user)
        view=DocumentViews.DocumentUploadView.as_view()

        with patch("documents.views.process_document.delay") as mock_func:

            response=view(request)
            mock_func.assert_not_called()
            assert response.status_code == 400
            assert response.data["title"][0].code == "blank"

        
    def test_DocumentUploadView_test_upload_numeric_title(self):

        factory=APIRequestFactory()
        
        pdf_cotent=b"we are checking if title is empty waht will happen"
        buffer=io.BytesIO(pdf_cotent)

        pdf_file=UploadedFile(
            name="checking_hr.pdf",
            content_type="application/pdf",
            file=buffer
        )

        data={
            "title":"123",
            "file":pdf_file
        }
        request=factory.post("api/v1/document/upload",data=data,format="multipart")
        force_authenticate(request,user=self.user)
        view=DocumentViews.DocumentUploadView.as_view()

        with patch("documents.views.process_document.delay") as mock_func:

            response=view(request)
            mock_func.assert_called_once()

            assert response.data["title"] == "123"
            assert response.status_code == 201

    def test_DocumentUploadView_test_upload_whitespace_title(self):
        factory=APIRequestFactory()
        
        pdf_cotent=b"we are checking if title is empty waht will happen"
        buffer=io.BytesIO(pdf_cotent)

        pdf_file=UploadedFile(
            name="checking_hr.pdf",
            content_type="application/pdf",
            file=buffer
        )

        data={
            "title":"    ",
            "file":pdf_file
        }
        request=factory.post("api/v1/document/upload",data=data,format="multipart")
        force_authenticate(request,user=self.user)
        view=DocumentViews.DocumentUploadView.as_view()

        with patch("documents.views.process_document.delay") as mock_func:

            response=view(request)
            mock_func.assert_not_called()
            assert response.status_code == 400
            assert response.data["title"][0].code == "blank"

    def test_DocumentUploadView_test_upload_long_title(self):
        factory=APIRequestFactory()
        
        pdf_cotent=b"we are checking if title is empty waht will happen"
        buffer=io.BytesIO(pdf_cotent)

        pdf_file=UploadedFile(
            name="checking_hr.pdf",
            content_type="application/pdf",
            file=buffer
        )

        data={
            "title":"sdsjadksadjksadnsajkdsandkjsdn1jk4n1jk24sfasfsafn12jk4njnasmasnfu4piporiwqporwqirpowqirwpoqriwqorpiwqropiwqrowqirwoqriwqoriwqropwqriwqoprwqidwnjnwjaxnjxan sanx sanxsxsnxbsjdskdjsdhsjkdsahjksancjksbcjaskbc",
            "file":pdf_file
        }
        request=factory.post("api/v1/document/upload",data=data,format="multipart")
        force_authenticate(request,user=self.user)
        view=DocumentViews.DocumentUploadView.as_view()

        with patch("documents.views.process_document.delay") as mock_func:

            response=view(request)
            mock_func.assert_not_called()
            assert response.status_code == 400
            assert response.data["title"][0].code == "max_length"


    def test_DocumentUploadView_test_no_pdf(self):

        factory=APIRequestFactory()
        data={
            "title":"Checker",
            "file":""
        }
        request=factory.post('document/api/v1/document/upload',data=data)
        force_authenticate(request,user=self.user)
        view=DocumentViews.DocumentUploadView.as_view()

        with patch("documents.views.process_document.delay") as mock_func:
            response=view(request)
            mock_func.assert_not_called()
            assert response.status_code == 400
            assert not Document.objects.filter(title="Checker").exists()
            
    def test_DocumentUploadView_test_empty_pdf(self):
    
        factory=APIRequestFactory()
        content=b''

        buffer=io.BytesIO(content)

        pdf_file=UploadedFile(
            name="checker.pdf",
            content_type="application/pdf",
            file=buffer
        )

        data={
            "title":"Checker",
            "file":pdf_file
        }
        request=factory.post('document/api/v1/document/upload',data=data,format="multipart")
        force_authenticate(request,user=self.user)
        view=DocumentViews.DocumentUploadView.as_view()

        with patch("documents.views.process_document.delay") as mock_func:
            response=view(request)
            mock_func.assert_not_called()
            assert response.status_code == 400
            assert not Document.objects.filter(title="Checker").exists()


    def test_DocumentUploadView_test_file_extensions(self):
        
        factory=APIRequestFactory()
        content=b'assafassfasfasfasfasfsavasvsavsa'

        buffer=io.BytesIO(content)

        pdf_file=UploadedFile(
            name="checker.txt",
            content_type="text/plain",
            file=buffer
        )

        data={
            "title":"Checker",
            "file":pdf_file
        }
        request=factory.post('document/api/v1/document/upload',data=data,format="multipart")
        force_authenticate(request,user=self.user)
        view=DocumentViews.DocumentUploadView.as_view()

        with patch("documents.views.process_document.delay") as mock_func:
            
            response=view(request)
            print(response.data)
            mock_func.assert_not_called()
            assert response.status_code == 400
            assert not Document.objects.filter(title="Checker").exists()