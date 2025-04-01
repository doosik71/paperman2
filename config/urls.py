from django.urls import path
from .views import *


urlpatterns = [
    path("", config_detail, name="config_detail"),
    path("detail/", config_detail, name="config_detail"),
]
