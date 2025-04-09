from django.urls import path
from .views import *

urlpatterns = [
    path("", topic_list, name="topic_list"),
    path("list/", topic_list, name="topic_list"),
    path("create/", topic_create, name="topic_create"),
    path('detail/<int:id>', topic_detail, name='topic_detail'),
    path('detail/<int:id>/<str:mode>/', topic_detail_mode, name='topic_detail_mode'),
    path('update/<int:id>', topic_update, name='topic_update'),
    path('delete/<int:id>', topic_delete, name='topic_delete'),
    path('citations/<int:id>', topic_citations, name='topic_citations'),
    path('collect_arxiv/', collect_arxiv, name='collect_arxiv'),
    path('collect_semantic_scholar/', collect_semantic_scholar, name='collect_semantic_scholar'),
]
