from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
import logger
import json
from google import genai
from openai import OpenAI


def home(request):
    return render(request, "home/home.html")


def get_status(_):
    return JsonResponse({"status": logger.status_message})


def request_genai(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            model = body.get("model", "").strip()
            key = body.get("key", "").strip()
            question = body.get("question", "").strip()

            logger.info("Asking genai with " + model)

            if key == "":
                return JsonResponse({"error": "Empty key."}, status=400)

            if question == "":
                return JsonResponse({"error": "Empty question."}, status=400)

            client = genai.Client(api_key=key)
            chat = client.chats.create(model=model)
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


def request_openrouter(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            model = body.get("model", "").strip()
            key = body.get("key", "").strip()
            question = body.get("question", "").strip()
            
            logger.info("Asking openrouter with " + model)
            
            if key == "":
                return JsonResponse({"error": "Empty key."}, status=400)

            if question == "":
                return JsonResponse({"error": "Empty question."}, status=400)

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=key,
            )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                stream=True
            )

            def stream_response():
                try:
                    for chunk in response:
                        if chunk:
                            yield chunk.choices[0].delta.content
                except Exception as e:
                    logger.info(str(e))

            return StreamingHttpResponse(
                stream_response(),
                content_type="text/plain",
                status=200,
            )
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=400)
