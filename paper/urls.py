from django.urls import path
from .views import *

urlpatterns = [
    path("", paper_list, name="paper_list"),
    path("list/", paper_list, name="paper_list"),
    path("create/", paper_create, name="paper_create"),
    path('detail/<int:id>/', paper_detail, name='paper_detail'),
    path('update/<int:id>/', paper_update, name='paper_update'),
    path('update_note/<int:id>/', paper_update_note, name='paper_update_note'),
    path('update_annnotation/<int:id>/', paper_update_annnotation, name='paper_update_annnotation'),
    path('pdf/<int:id>/', paper_pdf, name='paper_pdf'),
    path('editor/<int:id>/', paper_editor, name='paper_editor'),
    path('note/<int:id>/', paper_note, name='paper_note'),
    path('presentation/<int:id>/', paper_presentation, name='paper_presentation'),
    path("add/", paper_add, name="paper_add"),
    path("tag/", paper_tag, name="paper_tag"),
    path("citations/<int:id>/", paper_citations, name="paper_citations"),
    path("select_image/<int:id>/", select_image, name="select_image"),
    path("image/<int:id>/<int:page>/", get_image, name="get_image"),
]
