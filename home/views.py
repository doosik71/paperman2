import json
import hashlib
import io
import time
import tinylogger
import logging
import requests
import urllib.parse
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from google import genai
from openai import OpenAI
from config.models import *


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
            key = get_config_value("GEMINI_API_KEY")
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


def retrieve_pdf(url: str) -> bytes:
    """
    Retrieve PDF from a URL and cache it.
    """

    if not url or url == "":
        raise ValueError("Invalid URL")

    cache_key = hashlib.md5(url.encode("utf-8")).hexdigest()
    cached_pdf = cache.get(cache_key)

    if cached_pdf:
        tinylogger.info("Reading cached PDF")
        return cached_pdf
    else:
        tinylogger.info(f"Caching PDF from {url}")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://ieeexplore.ieee.org/",
            "Connection": "keep-alive",
        }
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        content = response.content
        
        print(content)
        cache.set(cache_key, content, timeout=60 * 60 * 24)
        return content


def get_pdf(request):
    """
    Get PDF.
    """

    url = urllib.parse.unquote(request.GET.get("url"))
    tinylogger.info(f"Getting PDF from {url}")

    try:
        content = retrieve_pdf(url)
    except Exception as e:
        message = f"Failed to fetch PDF: {e}"
        tinylogger.error(message)
        return HttpResponse(message, status=500)

    if not content:
        return HttpResponse("No PDF content", status=400)

    pdf_response = HttpResponse(content, content_type="application/pdf")
    pdf_response["Content-Disposition"] = "inline; filename=document.pdf"

    return pdf_response


def get_html(request) -> JsonResponse:
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


def get_json(request) -> JsonResponse:
    """
    Get JSON.
    """

    url = request.GET.get("url")
    params = {"fields": "title,authors,year,abstract,venue,citationCount,url"}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return JsonResponse(response.json(), status=200)
    else:
        return JsonResponse({"Error": response.text}, status=500)


def summarize_pdf(request):
    """
    Summarize PDF.
    """

    # Define chunk size (adjust as needed based on model limits)
    model = "gemini-2.0-flash-lite"
    CHUNK_SIZE = 15000

    url = request.GET.get("url")

    if not url:
        return JsonResponse({"Error": "No URL provided"}, status=400)

    try:
        tinylogger.info(f"Checking PDF from {url}")

        # Check if the URL is accessible
        response = requests.head(url)
        if response.status_code != 200:
            return JsonResponse({"Error": "URL is not accessible"}, status=400)

        # Check if the URL is a PDF
        content_type = response.headers.get("Content-Type", "")

        if "application/pdf" not in content_type:
            return JsonResponse({"Error": "URL is not a PDF"}, status=400)

        tinylogger.info(f"Reading PDF from {url}")

        # Fetch the PDF content
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        content = response.content

        # Extract text from PDF using pypdf
        tinylogger.info(f"Extracting PDF")

        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))  # Wrap content in BytesIO
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:  # Ensure text was extracted
                text += page_text + "\n\n"

        text_chunks = []
        current_chunk = ""
        # Split text into chunks, trying to preserve paragraphs/sentences
        for paragraph in text.split("\n\n"):
            if len(current_chunk) + len(paragraph) + 2 <= CHUNK_SIZE:
                current_chunk += paragraph + "\n\n"
            else:
                # If paragraph itself is too large, split it further (e.g., by sentence)
                if len(paragraph) > CHUNK_SIZE:
                    sentences = paragraph.split(". ")
                    temp_chunk = ""
                    for sentence in sentences:
                        if len(temp_chunk) + len(sentence) + 2 <= CHUNK_SIZE:
                            temp_chunk += sentence + ". "
                        else:
                            if temp_chunk:  # Add completed smaller chunk
                                text_chunks.append(temp_chunk.strip())
                            temp_chunk = sentence + ". "  # Start new smaller chunk
                    if temp_chunk:  # Add the last smaller chunk
                        text_chunks.append(temp_chunk.strip())
                else:
                    # Add the completed chunk and start a new one
                    if current_chunk:
                        text_chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n\n"

        # Add the last chunk if it's not empty
        if current_chunk:
            text_chunks.append(current_chunk.strip())

        if not text_chunks:  # Handle case where PDF has no extractable text
            return JsonResponse({"summary": "Could not extract text from PDF."})

        # Summarize text using Google genai API chunk by chunk
        key = get_config_value("GEMINI_API_KEY")
        if key == "":
            return JsonResponse({"error": "Empty key."}, status=400)

        client = genai.Client(api_key=key)
        combined_summary = ""

        tinylogger.info(f"Summarizing {len(text_chunks)} chunks...")

        for i, chunk_text in enumerate(text_chunks):
            tinylogger.info(f"Summarizing chunk {i+1}/{len(text_chunks)}")
            try:
                chat = client.chats.create(model=model)
                # Add context for subsequent chunks if needed (optional)
                prompt = f"Summarize the following text (part {i+1} of {len(text_chunks)}):\n{chunk_text}"
                response = chat.send_message_stream(prompt)
                chunk_summary = ""
                for resp_chunk in response:
                    if resp_chunk:
                        chunk_summary += resp_chunk.text
                combined_summary += (
                    chunk_summary + "\n\n"
                )  # Add separation between chunk summaries
                time.sleep(2)  # Optional: Add a delay to avoid rate limits
            except Exception as chunk_error:
                tinylogger.error(f"Error summarizing chunk {i+1}: {chunk_error}")
                combined_summary += f"[Error summarizing part {i+1}]\n\n"

        return JsonResponse({"summary": combined_summary.strip()})
    except requests.exceptions.RequestException as e:
        return JsonResponse({"Error": f"Request Error: {str(e)}"}, status=500)
    except ImportError:
        return JsonResponse(
            {"Error": "PyPDF not installed. Please install it."}, status=500
        )
    except Exception as e:
        tinylogger.error(f"General Error in summarize_pdf: {str(e)}")
        return JsonResponse(
            {"Error": f"An unexpected error occurred: {str(e)}"}, status=500
        )
