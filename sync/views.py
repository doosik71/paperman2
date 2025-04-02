import datetime
import logger
import os
import requests
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def sync_sync(request):
    """
    Sync dataset.
    """

    if request.method == "POST":
        try:
            address = request.POST["address"]
            port = request.POST["port"]
            url = f"http://{address}:{port}/sync/upload"
            file_path = "db.sqlite3"

            logger.info(url)
            
            with open(file_path, "rb") as f:
                response = requests.post(url, files={"file": f})

            message = f"Code: {response.status_code}, Message: {response.text}"
            messages.info(request, message)
            logger.info(message)
        except Exception as e:
            message = f"Error: {e}"
            messages.error(request, message)
            logger.error(message)

    return render(request, "sync/sync.html")


@csrf_exempt
def sync_upload(request):
    """
    Receive uploaded file and save to disk.
    """

    if request.method == "POST":
        try:
            uploaded_file = request.FILES.get("file")
            if not uploaded_file:
                return JsonResponse({"error": "No file provided"}, status=400)

            now = datetime.datetime.now()
            filename = now.strftime("db-%Y-%m-%d-%H-%M-%S.sqlite3")

            # 저장 경로 설정 (MEDIA_ROOT 또는 현재 디렉토리)
            save_path = os.path.join(settings.BASE_DIR, filename)

            with open(save_path, "wb") as out_file:
                for chunk in uploaded_file.chunks():
                    out_file.write(chunk)

            return JsonResponse({"message": "ok"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=405)

    return JsonResponse({"error": "Invalid request method"}, status=405)
