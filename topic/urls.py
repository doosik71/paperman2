from django.urls import path
from .views import topic_list, topic_create

urlpatterns = [
    path("", topic_list, name="topic_list"),
    path("create/", topic_create, name="topic_create"),
]
