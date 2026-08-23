from django.urls import path
from documents import views as documentviews

urlpatterns =[
    path('api/v1/document/upload',documentviews.DocumentUploadView.as_view(),name='document_upload'),
    path('api/v1/question/search',documentviews.QuestionSearchView.as_view(),name='question_search'),
    path('api/v1/documents/',documentviews.DocumentsListView.as_view(),name='documents'),
    path('api/v1/documents/<int:pk>/',documentviews.DocumentsRetreiveView.as_view(),name='document'),


]