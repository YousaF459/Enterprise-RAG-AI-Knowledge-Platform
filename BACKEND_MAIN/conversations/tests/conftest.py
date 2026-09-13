import pytest
from accounts.models import User
from organization.models import Organization
from conversations.models import Conversation


@pytest.fixture
def organization(db):
    organization=Organization.objects.create(name="Employee_organization",description="Creation of an organization")
    return organization


@pytest.fixture
def user_factory(db):
    def create_user(username="employee123",email="employee@gmail.com",password="employee123",role=User.Role.EMPLOYEE,organization=None):
        user=User.objects.create_user(username=username,email=email,password=password,role=role,organization=organization)
        return user
    return create_user



@pytest.fixture
def conversation_factory(db):
    def create_conversation(title="123",user=None):
        conversation=Conversation.objects.create(title=title,user=user)
        return conversation
    return create_conversation

    

    