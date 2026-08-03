from django.urls import path
from documents import views as documentviews

urlpatterns =[
    path('api/v1/document/upload',documentviews.DocumentUploadView.as_view(),name='document_upload'),
    path('api/v1/question/search',documentviews.QuestionSearchView.as_view(),name='question_search'),


]