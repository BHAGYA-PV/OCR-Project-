from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path("api/UploadDocument/", views.UploadDocument.as_view(), name="upload-document"),
    path("api/ListDocuments/", views.ListDocuments.as_view(), name="list-document"),
    path("api/SearchByName/", views.SearchByName.as_view(), name="SearchByName"),
    path("api/SearchByOCR/", views.SearchByOCR.as_view(), name="SearchByOCR"),

]