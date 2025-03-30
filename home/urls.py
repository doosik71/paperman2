from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("home/", home, name="home"),
    path("status/", get_status, name="get_status"),
    path("request_genai/", request_genai, name="request_genai"),
    path("request_openrouter/", request_openrouter, name="request_openrouter"),
]
