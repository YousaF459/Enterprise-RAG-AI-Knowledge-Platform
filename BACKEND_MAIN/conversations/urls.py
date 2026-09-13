from django.urls import path,include

## VIews COnversations
from conversations import views as ConversationViews


urlpatterns = [
    path("api/v1/",ConversationViews.ConversationView.as_view(),name="conversation_list_create"),
    path("api/v1/<int:pk>/",ConversationViews.ConversationDetailView.as_view(),name="conversation_retreive_delete"),
    path("<int:conversation_id>/messages/",ConversationViews.ConversationMessageCreateView.as_view(),name="conversation-message")
]