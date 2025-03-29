from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
import logger
import json
import requests
from google import genai


def home(request):
    return render(request, "home/home.html")


def get_status(_):
    return JsonResponse({"status": logger.status_message})


def gemini(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            key = body.get("key", "").strip()
            question = body.get("question", "").strip()

            if key == "":
                raise Exception("Empty key")

            if question == "":
                raise Exception("Empty question")

            client = genai.Client(api_key=key)
            chat = client.chats.create(model="gemini-2.0-flash")
            response = chat.send_message_stream(question)

            def stream_response():
                for chunk in response:
                    if chunk:
                        yield chunk.text

            return StreamingHttpResponse(
                stream_response(),
                content_type="text/plain",
                status=200,
            )
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=400)
