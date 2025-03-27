import json
import logger
import re
import requests
import time
from .models import Paper
from bs4 import BeautifulSoup
from datetime import datetime
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from paperman import settings
from topic.models import Topic
from urllib.parse import urlencode


def paper_list(request):
    """
    List all papers
    """

    if request.method == "POST":
        papers = Paper.objects.all()
        search = request.POST["search"]
        search_terms = [s.strip() for s in search.split() if s.strip()]

        for term in search_terms:
            if term != "":
                papers = papers.filter(
                    Q(author__icontains=term)
                    | Q(title__icontains=term)
                    | Q(abstract__icontains=term)
                )
                
        papers = papers.order_by("-citations")
    else:
        papers = []
        search = ""

    return render(
        request, "paper/paper_list.html", {"papers": papers, "search": search}
    )


def paper_create(request):
    """
    Create a new paper
    """

    topics = Topic.objects.all()
    topics = sorted(topics, key=lambda t: t.title)

    if request.method == "POST":
        try:
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
            abstract = request.POST["abstract"]
            note = request.POST["note"]

            if publish_date:
                publish_date = datetime.strptime(publish_date, "%Y-%m-%d")
                publish_date = timezone.make_aware(
                    publish_date, timezone.get_current_timezone()
                )
            else:
                publish_date = None

            if citations == "":
                citations = None

            paper = Paper.objects.create(
                title=title.strip(),
                author=author.strip(),
                publisher=publisher.strip(),
                publish_date=publish_date,
                doi=doi.strip(),
                url=url.strip(),
                pdf_url=pdf_url.strip(),
                pdf_name=pdf_name.strip(),
                citations=citations,
                tags=tags.strip(),
                abstract=abstract.strip(),
                note=note.strip(),
            )

            selected_topics = request.POST.getlist("topics")

            for topic_id in selected_topics:
                topic = Topic.objects.get(id=topic_id)
                paper.topics.add(topic)

            paper.save()

            message = f'Paper created: "{title}"'
            messages.success(request, message)
            logger.info(message)
            
            return redirect("paper_detail", paper.id)
        except Exception as e:
            message = f"Error: {e}"
            messages.error(request, message)
            logger.error(message)

    return render(request, "paper/paper_create.html", {"topics": topics})


def paper_detail(request, id):
    """
    Show a paper
    """

    paper = get_object_or_404(Paper, id=id)
    topics = Topic.objects.all()
    topic_ids = list(paper.topics.values_list("id", flat=True))
    topics = sorted(topics, key=lambda t: t.title)

    return render(
        request,
        "paper/paper_detail.html",
        {"paper": paper, "topics": topics, "topic_ids": topic_ids},
    )


def paper_pdf(request, id):
    """
    Show a paper PDF
    """

    paper = get_object_or_404(Paper, id=id)

    return render(request, "paper/paper_pdf.html", {"paper": paper})


def paper_note(request, id):
    """
    Show a paper note
    """

    paper = get_object_or_404(Paper, id=id)

    return render(
        request,
        "paper/paper_note.html",
        {
            "paper": paper,
            "LLM_REQUEST_URL": settings.LLM_REQUEST_URL,
            "LLM_MODEL": settings.LLM_MODEL,
            "GOOGLE_API_KEY": settings.GOOGLE_API_KEY,
        },
    )


def paper_update(request, id):
    """
    Update a paper
    """

    paper = get_object_or_404(Paper, id=id)
    message = None

    if request.method == "POST":
        try:
            paper.title = request.POST["title"].strip()
            paper.author = request.POST["author"].strip()
            paper.publisher = request.POST["publisher"].strip()
            publish_date = request.POST["publish_date"]
            paper.doi = request.POST["doi"].strip()
            paper.url = request.POST["url"].strip()
            paper.pdf_url = request.POST["pdf_url"].strip()
            paper.pdf_name = request.POST["pdf_name"].strip()
            paper.citations = request.POST["citations"].strip()
            paper.tags = request.POST["tags"].strip()
            paper.abstract = request.POST["abstract"].strip()
            paper.note = request.POST["note"].strip()

            if publish_date:
                publish_date = datetime.strptime(publish_date, "%Y-%m-%d")
                publish_date = timezone.make_aware(
                    publish_date, timezone.get_current_timezone()
                )
            else:
                publish_date = None

            if paper.citations == "":
                paper.citations = None

            selected_topics = request.POST.getlist("topics")
            paper.topics.clear()

            for topic_id in selected_topics:
                topic = Topic.objects.get(id=topic_id)
                paper.topics.add(topic)

            paper.save()

            message = f'Paper updated: "{paper.title}"'
            messages.success(request, message)
            logger.info(message)
        except Exception as e:
            message = f"Error: {e}"
            messages.error(request, message)
            logger.error(message)

    return redirect("paper_detail", id)


def paper_update_note(request, id):
    """
    Update a paper note
    """

    paper = get_object_or_404(Paper, id=id)

    if request.method == "POST":
        paper.note = request.POST["note"].strip()

        paper.save()

        message = f'Paper\'s note updated: "{paper.title}"'
        messages.success(request, message)
        logger.info(message)

    return render(request, "paper/paper_note.html", {"paper": paper})


def paper_add(request):
    """
    Add a paper to the database
    """

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

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
        abstract = data.get("abstract")
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
                title=title.strip(),
                author=author.strip(),
                publisher=publisher.strip(),
                publish_date=publish_date,
                doi=doi.strip(),
                url=url.strip(),
                pdf_url=pdf_url.strip(),
                pdf_name=pdf_name.strip(),
                citations=citations,
                tags=tags.strip(),
                abstract=abstract.strip(),
                note=note.strip(),
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

        logger.info(f"Paper added to topic: {p.title} -> {topic.title}")
    except:
        return JsonResponse({"error": f"Failed to add paper to topic"}, status=500)

    return JsonResponse({"message": "Paper added successfully"}, status=201)


def paper_tag(request):
    """
    Toggle a paper tag
    """

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

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

        p.tags = p.tags.strip()
        p.save()

        return JsonResponse({"message": "Tag toggled", "tags": p.tags}, status=200)
    except Paper.DoesNotExist:
        return JsonResponse({"error": "Paper not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Failed to toggle tag: {str(e)}"}, status=500)


def paper_citations(request, id):
    """
    Update paper's citations by using semantic scholar.
    """

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    paper = get_object_or_404(Paper, id=id)
    response, paper = update_paper_citations(paper)

    if response.status_code == 200:
        return JsonResponse({"citations": paper.citations}, status=200)
    else:
        return JsonResponse({"citations": 0}, status=400)


def update_paper_citations(paper):
    """
    Update paper citations
    """

    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = urlencode(
        {"query": paper.author + ", " + paper.title, "fields": "title,citationCount"}
    )

    for _ in range(10):
        response = requests.get(f"{base_url}?{params}")
        if response.status_code == 200:
            break
        else:
            time.sleep(1)

    if response.status_code == 200:
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            paper.citations = data["data"][0].get("citationCount", 0)

            try:
                paper.save()
                logger.info(f'{paper.citations} citation(s) for "{paper.title}"')
                return response, paper
            except Exception as e:
                logger.error(e)

    paper.citations = 0
    paper.save()
    logger.info(f'No citation for "{paper.title}"')

    return response, paper


def paper_citations_google_scholar(request):
    """
    Update paper's citations by using google scholar. (INCOMPLETE)
    """

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        paper_id = data.get("paper_id")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    paper = get_object_or_404(Paper, id=paper_id)
    query = {
        "hl": "en",
        "as_sdt": "0,5",
        "q": paper.author + ", " + paper.title,
        "btnG": "",
    }
    query = urlencode(query).replace("%22", '"')
    url = "https://scholar.google.com/scholar?" + query
    logger.info(url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        logger.info(response.text)
        soup = BeautifulSoup(response.text, "html.parser")
        gs_ri_divs = soup.find_all("div", class_="gs_ri")
        logger.info(gs_ri_divs)

        if gs_ri_divs:
            gs_ri_html = [str(div) for div in gs_ri_divs]

            if len(gs_ri_html) > 0:
                match = re.search(r">Cited by (\d+)<", gs_ri_html[0])

                if match:
                    paper.citations = int(match.group(1))

                    try:
                        paper.save()
                    except Exception as e:
                        logger.error(e)

                    return JsonResponse({"citations": paper.citations}, status=200)

    return JsonResponse({"citations": 0}, status=400)
