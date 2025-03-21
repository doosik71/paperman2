import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Paper
from datetime import datetime


def paper_list(request):
    papers = Paper.objects.all().order_by("-publish_date")
    return render(request, "paper/paper_list.html", {"papers": papers})


def paper_create(request):
    if request.method == "POST":
        title = request.POST["title"]
        author = request.POST["author"]
        publisher = request.POST["publisher"]
        publish_date = request.POST["publish_date"]
        doi = request.POST["doi"]
        url = request.POST["url"]
        pdf_url = request.POST["pdf_url"]
        pdf_name = request.POST["pdf_name"]
        citations = request.POST["citations"]
        tags = request.POST["tags"]
        note = request.POST["note"]

        publish_date = datetime.strptime(publish_date, "%Y-%m-%d")
        publish_date = timezone.make_aware(
            publish_date, timezone.get_current_timezone()
        )

        Paper.objects.create(
            title=title,
            author=author,
            publisher=publisher,
            publish_date=publish_date,
            doi=doi,
            url=url,
            pdf_url=pdf_url,
            pdf_name=pdf_name,
            citations=citations,
            tags=tags,
            note=note,
        )

        return redirect("paper_list")
    return render(request, "paper/paper_create.html")


def paper_add(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title")
            author = data.get("author")
            publisher = data.get("publisher")
            publish_date = data.get("publish_date")
            doi = data.get("doi")
            url = data.get("url")
            pdf_url = data.get("pdf_url")
            pdf_name = data.get("pdf_name")
            citations = data.get("citations")
            tags = data.get("tags")
            note = data.get("note")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if not title:
            return JsonResponse({"error": "Title is required"}, status=400)

        if not author:
            return JsonResponse({"error": "Author is required"}, status=400)

        if not url:
            return JsonResponse({"error": "Url is required"}, status=400)

        if not pdf_url:
            return JsonResponse({"error": "PDF url is required"}, status=400)

        try:
            publish_date = datetime.strptime(publish_date, "%Y-%m-%d")
            publish_date = timezone.make_aware(
                publish_date, timezone.get_current_timezone()
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Invalid publish_date format: {str(e)}"}, status=400
            )

        try:
            Paper.objects.create(
                title=title,
                author=author,
                publisher=publisher,
                publish_date=publish_date,
                doi=doi,
                url=url,
                pdf_url=pdf_url,
                pdf_name=pdf_name,
                citations=citations,
                tags=tags,
                note=note,
            )

            return JsonResponse({"message": "Paper added successfully"}, status=201)
        except Exception as e:
            print("errr", e)
            return JsonResponse(
                {"error": f"Failed to create paper: {str(e)}"}, status=500
            )

    return JsonResponse({"error": "Invalid request method"}, status=405)
