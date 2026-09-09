import pytest
from rest_framework.test import APIRequestFactory,force_authenticate
from django.core.files.uploadedfile import UploadedFile
from unittest.mock import patch
import io
from documents.tasks import process_document


## Document Views and Model imported
from documents.models import Document
from documents.views import DocumentUploadView,DocumentsRetrieveView


## USer App Views
from accounts.models import User



## Checking Title Validation For Document
@pytest.mark.parametrize(
    "title,file_name,content_types,expected_status",
    [
        ("","policy.pdf","application/pdf", 400),
        ("   ","policy.pdf","application/pdf", 400),
        ("123","policy.pdf","application/pdf", 201),
        ("123","policy.txt","text/plain", 400)
    ]
)
def test_multiple_title_inputs(title,file_name,content_types,expected_status,user):

    factory=APIRequestFactory()
    content=b"This is testing file we are using mutiple validations"
    buffer=io.BytesIO(content)
    pdf_file=UploadedFile(
        name=file_name,
        content_type=f"{content_types}",
        file=buffer   
    )
    data={
        "title":title,
        "file":pdf_file
    }
    request=factory.post('api/v1/document/upload',format="multipart",data=data)
    force_authenticate(request,user=user)
    view=DocumentUploadView.as_view()

    with patch("documents.views.process_document.delay") as mock_object:
        response=view(request)
        assert response.status_code == expected_status



@pytest.mark.parametrize(
    "username,email,password,role",[
        ("employee123","employee@gmail.com","employee123",User.Role.EMPLOYEE),
        ("admin123","admin@gmail.com","admin123",User.Role.ORG_ADMIN),
        ("sadmin123","sadmin@gmail.com","sadmin123",User.Role.SUPER_ADMIN),
    ]
)
def test_user(username,email,password,role,user_factory):

    user=user_factory(username=username,email=email,password=password,role=role)

    assert user.email == email
    assert user.role == role

    


@pytest.mark.parametrize(
    "username,email,password,role,expectedStatus",[
        ("employee123","employee@gmail.com","employee123",User.Role.EMPLOYEE,403),
        ("admin123","admin@gmail.com","admin123",User.Role.ORG_ADMIN,200),
        ("sadmin123","sadmin@gmail.com","sadmin123",User.Role.SUPER_ADMIN,200),
    ]
)
def test_user_permissions(username,email,password,role,expectedStatus,user_factory,organization,document):
    
    user=user_factory(username=username,email=email,password=password,role=role,organization=organization)
    factory=APIRequestFactory()
    request=factory.get(f"api/v1/documents/{document.id}/")
    view=DocumentsRetrieveView.as_view()
    force_authenticate(request,user=user)
    response=view(request,pk=document.id)

    assert response.status_code == expectedStatus



def test_document_created(documentCreated):

    assert documentCreated.title == "NEW_HR_POLICY"


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a/b


def test_checkingPytestRaise():
    with pytest.raises(ValueError) as exc_info:
        divide(10,0)

    assert exc_info.value.args[0] == "Cannot divide by zero"