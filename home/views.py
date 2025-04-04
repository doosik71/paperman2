import json
import hashlib
import tinylogger
import logging
import requests
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from google import genai
from openai import OpenAI


logging.disable(logging.INFO)


def home(request):
    """
    Get home page.
    """

    return render(request, "home/home.html")


def get_status(_):
    """
    Get server status.
    """

    return JsonResponse({"status": tinylogger.status_message})


def request_genai(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            model = body.get("model", "").strip()
            key = body.get("key", "").strip()
            question = body.get("question", "").strip()

            tinylogger.info("Asking genai with " + model)

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

            tinylogger.info("Asking openrouter with " + model)

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
                messages=[{"role": "user", "content": question}],
                stream=True,
            )

            def stream_response():
                try:
                    for chunk in response:
                        if chunk:
                            yield chunk.choices[0].delta.content
                except Exception as e:
                    tinylogger.info(str(e))

            return StreamingHttpResponse(
                stream_response(),
                content_type="text/plain",
                status=200,
            )
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=400)


def get_pdf(request):
    """
    Get PDF.
    """

    url = request.GET.get("url")

    if not url:
        return HttpResponse("No PDF URL provided", status=400)

    cache_key = hashlib.md5(url.encode("utf-8")).hexdigest()
    cached_pdf = cache.get(cache_key)

    if cached_pdf:
        pdf_response = HttpResponse(cached_pdf, content_type="application/pdf")
        pdf_response["Content-Disposition"] = "inline; filename=document.pdf"
        return pdf_response

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        content = response.content
        cache.set(cache_key, content, timeout=60 * 60 * 24)
        pdf_response = HttpResponse(content, content_type="application/pdf")
        pdf_response["Content-Disposition"] = "inline; filename=document.pdf"

        return pdf_response

    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Failed to fetch PDF: {e}", status=500)


def get_html(request):
    """
    Get HTML.
    """

    url = request.GET.get("url")

    if not url:
        return JsonResponse({"Error": "No URL provided"}, status=400)

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return JsonResponse({"html": response.text})
    except requests.exceptions.RequestException as e:
        return JsonResponse({"Error": str(e)}, status=500)
