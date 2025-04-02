from django.urls import path
from .views import *


urlpatterns = [
    path("", sync_sync, name="sync_sync"),
    path("upload", sync_upload, name="sync_upload"),
]
