# pdf_project/qa/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('upload_and_list/', views.upload_and_list_files, name='upload_and_list_files'),
    path('process_pages/<int:file_id>/', views.process_pages, name='process_pages'),
    path('view_duplicates/<int:file_id>/', views.view_duplicates, name='view_duplicates'),
    path('mark_duplicate/', views.mark_duplicate, name='mark_duplicate'),
]
