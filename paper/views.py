import json
import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Paper
from topic.models import Topic
from datetime import datetime


logger = logging.getLogger(__name__)


def paper_list(request):
    """
    List all papers
    """

    papers = Paper.objects.all().order_by("-publish_date")
    return render(request, "paper/paper_list.html", {"papers": papers})


def paper_create(request):
    """
    Create a new paper
    """

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
    """
    Add a paper to the database
    """

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
            topic_id = data.get("topic_id")
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

        if Paper.objects.filter(url=url).exists():
            p = Paper.objects.get(url=url)
        else:
            try:
                p = Paper.objects.create(
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
            except Exception as e:
                logger.error("Error:", e)

                return JsonResponse(
                    {"error": f"Failed to create paper: {str(e)}"}, status=500
                )

        try:
            topic = Topic.objects.get(id=topic_id)
            p.topics.add(topic)
            p.save()
        except:
            return JsonResponse({"error": f"Failed to add paper to topic"}, status=500)

        return JsonResponse({"message": "Paper added successfully"}, status=201)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def paper_tag(request):
    """
    Toggle a paper tag
    """

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            paper_id = data.get("paper_id")
            tag = data.get("tag")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if not paper_id:
            return JsonResponse({"error": "Paper ID is required"}, status=400)

        if not tag:
            return JsonResponse({"error": "Tag is required"}, status=400)

        try:
            p = Paper.objects.get(id=paper_id)
            if tag in p.tags:
                p.tags = p.tags.replace(tag, "")
            else:
                p.tags += tag

            p.save()

            return JsonResponse({"message": "Tag toggled", "tags": p.tags}, status=200)
        except Paper.DoesNotExist:
            return JsonResponse({"error": "Paper not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Failed to toggle tag: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
