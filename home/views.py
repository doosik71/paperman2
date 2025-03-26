from django.shortcuts import render
from django.http import JsonResponse
import logger


def home(request):
    return render(request, "home/home.html")


def get_status(_):
    return JsonResponse({"status": logger.status_message})
