from django.urls import path
from .views import *

urlpatterns = [
    path("", topic_list, name="topic_list"),
    path("create/", topic_create, name="topic_create"),
    path('detail/<int:id>', topic_detail, name='topic_detail'),
    path('update/<int:id>', topic_update, name='topic_update'),
    path('delete/<int:id>', topic_delete, name='topic_delete'),
]
