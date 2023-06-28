from django.urls import path
from llamaapp.views import upload_document, process_document, home

urlpatterns = [
    path('home', home, name='home'),
    path('', upload_document, name='upload'),
    path('upload', upload_document, name='upload'),
    path('process', process_document, name='process'),
]