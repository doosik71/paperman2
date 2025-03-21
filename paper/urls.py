from django.urls import path
from .views import *

urlpatterns = [
    path("", paper_list, name="paper_list"),
    path("create/", paper_create, name="paper_create"),
    path('detail/<int:id>', paper_detail, name='paper_detail'),
    path('update/<int:id>', paper_update, name='paper_update'),
    path('pdf/<int:id>', paper_pdf, name='paper_pdf'),
    path("add/", paper_add, name="paper_add"),
    path("tag/", paper_tag, name="paper_tag"),
]
