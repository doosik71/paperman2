from django.urls import path
from .views import paper_list, paper_create

urlpatterns = [
    path("", paper_list, name="paper_list"),
    path("create/", paper_create, name="paper_create"),
]
