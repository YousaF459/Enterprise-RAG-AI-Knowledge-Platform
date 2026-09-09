## LIBRARY
import pytest
import io
from django.core.files.uploadedfile import UploadedFile
 
## MODELS
from documents.models import Document
from accounts.models import User
from organization.models import Organization


@pytest.fixture
def organization(db):
    organization=Organization.objects.create(name="yousaf",description="Yousaf company")
    return organization


@pytest.fixture
def user(organization):
    user=User.objects.create_user(username="yousaf123",email="yousaf@gmail.com",password="yousaf123",organization=organization,role=User.Role.ORG_ADMIN)
    return user

@pytest.fixture
def document(user,organization):

    content=b"MY name is Yousaf and i am Backend AI developer"
    buffer=io.BytesIO(content)

    pdf_File=UploadedFile(
        name="NEW_HR_POLICY.pdf",
        content_type="application/pdf",
        file=buffer
    )


    document=Document.objects.create(title="NEW_HR_POLICY",file=pdf_File,organization=organization,uploaded_by=user)
    return document


@pytest.fixture(scope="class",autouse=True)
def setup():
    print("SETUP RUN")



@pytest.fixture
def organization_factory(db):
    def create_organization(name="org123",description="org123_desc"):
        organization=Organization.objects.create(name=name,description=description)
        return organization
    return create_organization



@pytest.fixture
def user_factory(db):
    def create_user(username="new123",email="new@gmail.com",password="new123",organization=None,role=User.Role.EMPLOYEE):
        user=User.objects.create_user(username=username,email=email,password=password,organization=organization,role=role)
        return user
    return create_user


@pytest.fixture
def documentCreated(organization,user):

    content=b"MY name is Yousaf and i am Backend AI developer"
    buffer=io.BytesIO(content)

    pdf_File=UploadedFile(
        name="NEW_HR_POLICY.pdf",
        content_type="application/pdf",
        file=buffer
    )


    document=Document.objects.create(title="NEW_HR_POLICY",file=pdf_File,organization=organization,uploaded_by=user)

    yield document

    document.delete()

    

    