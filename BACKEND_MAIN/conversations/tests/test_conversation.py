import pytest
from accounts.models import User
from conversations.models import Conversation
from rest_framework.test import APIRequestFactory,force_authenticate
from conversations.views import ConversationView,ConversationDetailView

# test to check title validationsin
@pytest.mark.parametrize(
        "user_role,title,expected_status",[
            (User.Role.EMPLOYEE,"new creation",201),
            (User.Role.EMPLOYEE,"",400),
            (User.Role.EMPLOYEE,"  ",400),
        ]
)
def test_conversation_validation(user_role,title,expected_status,organization,user_factory):

    user=user_factory(username="employee123",email="employee@gmail.com",password="employee123",role=user_role,organization=organization)
    factory=APIRequestFactory()
    data={
        "title":title
    }
    request=factory.post("conversation/api/v1/",data=data,format="json")
    force_authenticate(request,user=user)
    view=ConversationView.as_view()
    response=view(request)

    assert response.status_code == expected_status



# test to check permissions according to user role
@pytest.mark.parametrize(
        "user_role,title,expected_status",[
            (User.Role.EMPLOYEE,"new creation",201),
            (User.Role.ORG_ADMIN,"new creation",403),
            (User.Role.SUPER_ADMIN,"new creation",403),
        ]
)
def test_conversation_permission(user_role,title,expected_status,organization,user_factory):

    user=user_factory(username="employee123",email="employee@gmail.com",password="employee123",role=user_role,organization=organization)
    factory=APIRequestFactory()
    data={
        "title":title
    }
    request=factory.post("conversation/api/v1/",data=data,format="json")
    force_authenticate(request,user=user)
    view=ConversationView.as_view()
    response=view(request)

    assert response.status_code == expected_status


# test to check list of all conversations
def test_conversation_lists(user_factory,conversation_factory,organization):

    user=user_factory(username="employee123",email="employee@gmail.com",password="employee123",role=User.Role.EMPLOYEE,organization=organization)
    conversation1=conversation_factory(title="Conversation 1 title",user=user)
    conversation2=conversation_factory(title="Conversation 2 title",user=user)
    conversation3=conversation_factory(title="Conversation 3 title",user=user)


    factory=APIRequestFactory()
    request=factory.get("conversation/api/v1/")
    force_authenticate(request,user=user)
    view=ConversationView.as_view()
    response=view(request)

    assert response.status_code == 200
    assert len(response.data) != 0



# test to check if  employee cannot see conversation of other employee
def test_conversation_employee_privacy(user_factory,conversation_factory,organization):

    user1=user_factory(username="employee123",email="employee@gmail.com",password="employee123",role=User.Role.EMPLOYEE,organization=organization)
    user2=user_factory(username="employee2",email="employee2@gmail.com",password="employee12",role=User.Role.EMPLOYEE,organization=organization)

    conversation1=conversation_factory(title="Conversation 1 title",user=user1)
    conversation2=conversation_factory(title="Conversation 2 title",user=user1)
    conversation3=conversation_factory(title="Conversation 3 title",user=user1)


    factory=APIRequestFactory()
    request=factory.get("conversation/api/v1/")
    force_authenticate(request,user=user2)
    view=ConversationView.as_view()
    response=view(request)

    assert response.status_code == 200
    assert len(response.data) == 0



# test to check if a conversation can be retreived
def test_conversation_retreival(user_factory,conversation_factory,organization):

    user=user_factory(username="employee123",email="employee@gmail.com",password="employee123",role=User.Role.EMPLOYEE,organization=organization)

    conversation1=conversation_factory(title="Conversation 1 title",user=user)
    conversation2=conversation_factory(title="Conversation 2 title",user=user)
    conversation3=conversation_factory(title="Conversation 3 title",user=user)


    factory=APIRequestFactory()
    request=factory.get(f"conversation/api/v1/{conversation1.id}/")
    force_authenticate(request,user=user)
    view=ConversationDetailView.as_view()
    response=view(request,pk=conversation1.id)

    assert response.status_code == 200
    assert response.data["title"] == "Conversation 1 title"
    

# test to check if a conversation can be deleted
def test_conversation_deletion(user_factory,conversation_factory,organization):

    user=user_factory(username="employee123",email="employee@gmail.com",password="employee123",role=User.Role.EMPLOYEE,organization=organization)

    conversation1=conversation_factory(title="Conversation 1 title",user=user)
    conversation2=conversation_factory(title="Conversation 2 title",user=user)
    conversation3=conversation_factory(title="Conversation 3 title",user=user)


    factory=APIRequestFactory()
    request=factory.delete(f"conversation/api/v1/{conversation1.id}/")
    force_authenticate(request,user=user)
    view=ConversationDetailView.as_view()
    response=view(request,pk=conversation1.id)

    assert response.status_code == 204
    assert not Conversation.objects.filter(id=conversation1.id).exists()
