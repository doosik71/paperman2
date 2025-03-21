from django.urls import path
from .views import *

urlpatterns = [
    path("", paper_list, name="paper_list"),
    path("create/", paper_create, name="paper_create"),
    path("add/", paper_add, name="paper_add"),
    path("tag/", paper_tag, name="paper_tag"),
]
