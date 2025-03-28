from django.shortcuts import render
from django.http import JsonResponse
import logger
import json
import requests


def home(request):
    return render(request, "home/home.html")


def get_status(_):
    return JsonResponse({"status": logger.status_message})


def proxy(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            url = body.get("url")
            headers = body.get("headers", {})
            data = body.get("data", {})

            if not url:
                return JsonResponse({"error": "Missing url"}, status=400)

            if headers:
                headers = json.loads(headers) if isinstance(headers, str) else headers

            if data:
                data = json.loads(data) if isinstance(data, str) else data

            response = requests.post(url, headers=headers, json=data)

            return JsonResponse(response.json(), status=response.status_code)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid headers or data"}, status=400)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=400)
