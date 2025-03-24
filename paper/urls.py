from django.urls import path
from .views import *

urlpatterns = [
    path("list/", paper_list, name="paper_list"),
    path("create/", paper_create, name="paper_create"),
    path('detail/<int:id>', paper_detail, name='paper_detail'),
    path('update/<int:id>', paper_update, name='paper_update'),
    path('update_note/<int:id>', paper_update_note, name='paper_update_note'),
    path('pdf/<int:id>', paper_pdf, name='paper_pdf'),
    path('note/<int:id>', paper_note, name='paper_note'),
    path("add/", paper_add, name="paper_add"),
    path("tag/", paper_tag, name="paper_tag"),
    path("citations/", paper_citations, name="paper_citations"),
]
