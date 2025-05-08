import json
import tinylogger
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET
import queue
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic
from paper.models import Paper
from paper.views import update_paper_citations, add_paper_to_topic


topic_task_queue = queue.Queue()
topic_thread_running = False


def topic_list(request) -> HttpResponse:
    """
    List all topics.
    """

    topics = Topic.objects.all().order_by("title")

    for topic in topics:
        papers = Paper.objects.filter(topics=topic)
        topic.paper_count = papers.count()
        topic.citation_count = papers.filter(citations__isnull=False).count()
        topic.tags_count = papers.exclude(tags="").exclude(tags__isnull=True).count()
        topic.star_count = papers.filter(tags__icontains="⭐").count()
        topic.note_count = papers.exclude(note="").count()

    return render(request, "topic/topic_list.html", {"topics": topics})


@login_required
def topic_create(request) -> HttpResponse:
    """
    Create a new topic.
    """

    if request.method == "POST":
        title = request.POST["title"]
        keywords = request.POST["keywords"]

        if Topic.objects.filter(title=title).exists():
            topic = Topic.objects.get(title=title)

            return redirect("topic_detail", topic.id)

        Topic.objects.create(title=title, keywords=keywords)

        message = f'Topic created: "{title}"'
        messages.success(request, message)
        tinylogger.info(message)

        return redirect("topic_list")

    return render(request, "topic/topic_create.html")


def topic_detail(request, id) -> HttpResponse:
    """
    Show a topic and its papers.
    """

    return topic_detail_mode(request, id, None)


def topic_detail_mode(request, id, mode) -> HttpResponse:
    """
    Show a topic and its papers.
    """

    topic = get_object_or_404(Topic, id=id)
    papers = Paper.objects.filter(topics=topic)

    if mode == "cited":
        papers = papers.filter(citations__isnull=False)
    elif mode == "tagged":
        papers = papers.exclude(tags="").exclude(tags__isnull=True)
    elif mode == "starred":
        papers = papers.filter(tags__icontains="⭐")
    elif mode == "noted":
        papers = papers.exclude(note="")

    papers = papers.order_by("-citations")

    return render(
        request, "topic/topic_detail.html", {"topic": topic, "papers": papers}
    )


@login_required
def topic_update(request, id) -> HttpResponse:
    """
    Update a topic.
    """

    topic = get_object_or_404(Topic, id=id)

    if request.method == "POST":
        title = request.POST["title"]
        keywords = request.POST["keywords"]

        topic = get_object_or_404(Topic, id=id)
        topic.title = title
        topic.keywords = keywords
        topic.save()

        message = f'Topic updated: "{title}"'
        messages.success(request, message)
        tinylogger.info(message)

    return redirect("topic_detail", id)


@login_required
def topic_delete(request, id):
    """
    Delete a topic.
    """

    topic = get_object_or_404(Topic, id=id)

    if request.method == "POST":
        topic.delete()

        message = f'Topic deleted: "{topic.title}"'
        messages.success(request, message)
        tinylogger.info(message)

    return redirect("topic_list")


@login_required
def topic_citations(request, id) -> JsonResponse:
    """
    Update citations for all papers in topic.
    """

    global topic_thread_running

    topic = get_object_or_404(Topic, id=id)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    # 작업을 큐에 추가
    topic_task_queue.put(topic)

    tinylogger.info(f'Queueing citations on the topic: "{topic.title}"')

    # 스레드가 실행 중이 아니면 새로 시작
    if not topic_thread_running:
        topic_thread_running = True

        def thread_target():
            global topic_thread_running
            try:
                while not topic_task_queue.empty():
                    current_topic = topic_task_queue.get()
                    __update_topic_citations(current_topic)
                    topic_task_queue.task_done()
            finally:
                topic_thread_running = False

        topic_thread = threading.Thread(target=thread_target)
        topic_thread.start()

    return JsonResponse({"message": "Topic added to the queue."}, status=200)


def __update_topic_citations(topic):
    """
    Updates the citation counts for all papers belonging to the toic.
    """

    papers = Paper.objects.filter(topics=topic, citations__isnull=True)
    count = len(papers)

    tinylogger.info(f'Updating citations on the topic: "{topic.title}"')

    for index, paper in enumerate(papers):
        tinylogger.info(f"Processing {index + 1:,} of {count:,}")
        update_paper_citations(paper)
        time.sleep(1)

    tinylogger.info(f'Complete citations on the topic: "{topic.title}"')


@login_required
def collect_arxiv(request) -> JsonResponse:
    """
    Collect papers from Arxiv.
    """

    if request.method == "POST":
        try:
            body = json.loads(request.body)
            topic_id = body.get("topic_id", "")
            keywords = body.get("keywords", "")
            max_results = int(body.get("max_results", 0))

            if topic_id == "":
                raise Exception("Invalid topic id")

            if keywords == "":
                raise Exception("Invalid keywords")

            if max_results == 0:
                raise Exception("Invalid max_results")

            threading.Thread(
                target=__collect_arxiv, args=(topic_id, keywords, max_results)
            ).start()

            return JsonResponse({"message": "ok"}, status=200)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=400)


def __collect_arxiv(topic_id: int, keywords: str, max_results: int) -> None:
    if not keywords.strip():
        raise ValueError("Keywords are required!")

    keyword_list = [k.strip() for k in keywords.split(",")]
    count = 0

    for keyword in keyword_list:
        papers = __get_arxiv_list(keyword, max_results)

        for paper in papers:
            try:
                title = paper.find("{http://www.w3.org/2005/Atom}title").text
                authors = ", ".join(
                    a.find("{http://www.w3.org/2005/Atom}name").text
                    for a in paper.findall("{http://www.w3.org/2005/Atom}author")
                )
                publisher = "arXiv"
                publish_date = paper.find(
                    "{http://www.w3.org/2005/Atom}published"
                ).text.split("T")[0]
                doi = ""
                url = paper.find("{http://www.w3.org/2005/Atom}id").text
                abstract = paper.find("{http://www.w3.org/2005/Atom}summary").text
                pdf_url = url.replace("/abs/", "/pdf/")
                pdf_name = title.replace(" ", "_") + ".pdf"
                citations = None
                tags = ""
                note = ""

                add_paper_to_topic(
                    title,
                    authors,
                    publisher,
                    publish_date,
                    doi,
                    url,
                    pdf_url,
                    pdf_name,
                    citations,
                    tags,
                    abstract,
                    note,
                    topic_id,
                )

                count += 1
            except Exception as e:
                print(f'Error while processing paper "{title}": {e}')

    tinylogger.info(f"{count:,} papers are added")


def __get_arxiv_list(keywords: str, max_results: int) -> list:
    """
    Get paper list from Arxiv.
    """

    research_topic = keywords.replace(" ", "+")
    url = (
        f"https://export.arxiv.org/api/query?search_query=all:{research_topic}&start=0"
        + f"&max_results={max_results}&sortBy=relevance&sortOrder=descending"
    )

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
        root = ET.fromstring(data)
        return root.findall(".//{http://www.w3.org/2005/Atom}entry")
    except Exception as e:
        print(f"Error fetching arXiv data: {e}")
        return []


@login_required
def collect_semantic_scholar(request) -> JsonResponse:
    """
    Collect papers from Semantic Scholar.
    """

    if request.method == "POST":
        try:
            body = json.loads(request.body)
            topic_id = body.get("topic_id", "")
            keywords = body.get("keywords", "")
            max_results = int(body.get("max_results", 0))

            if topic_id == "":
                raise Exception("Invalid topic id")

            if keywords == "":
                raise Exception("Invalid keywords")

            if max_results == 0:
                raise Exception("Invalid max_results")

            threading.Thread(
                target=__collect_semantic_scholar,
                args=(topic_id, keywords, max_results),
            ).start()

            return JsonResponse({"message": "ok"}, status=200)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=400)


def __collect_semantic_scholar(topic_id: int, keywords: str, max_results: int) -> None:
    if not keywords.strip():
        raise ValueError("Keywords are required!")

    keyword_list = [k.strip() for k in keywords.split(",")]
    count = 0

    for keyword in keyword_list:
        papers = __get_semantic_scholar_list(keyword, max_results)

        for paper in papers:
            try:
                title = paper.find("{http://www.w3.org/2005/Atom}title").text
                authors = ", ".join(
                    a.find("{http://www.w3.org/2005/Atom}name").text
                    for a in paper.findall("{http://www.w3.org/2005/Atom}author")
                )
                publisher = "arXiv"
                publish_date = paper.find(
                    "{http://www.w3.org/2005/Atom}published"
                ).text.split("T")[0]
                doi = ""
                url = paper.find("{http://www.w3.org/2005/Atom}id").text
                abstract = paper.find("{http://www.w3.org/2005/Atom}summary").text
                pdf_url = url.replace("/abs/", "/pdf/")
                pdf_name = title.replace(" ", "_") + ".pdf"
                citations = None
                tags = ""
                note = ""

                add_paper_to_topic(
                    title,
                    authors,
                    publisher,
                    publish_date,
                    doi,
                    url,
                    pdf_url,
                    pdf_name,
                    citations,
                    tags,
                    abstract,
                    note,
                    topic_id,
                )

                count += 1
            except Exception as e:
                print(f'Error while processing paper "{title}": {e}')

    tinylogger.info(f"{count:,} papers are added")


def __get_semantic_scholar_list(keywords: str, max_results: int) -> list:
    """
    Get paper list from Semantic Scholar.
    """

    research_topic = keywords.replace(" ", "+")
    fields = 'title,authors,url,publicationVenue.name,abstract,publicationDate,citationCount,openAccessPdf.url,externalIds.DOI'
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={research_topic}&fields={fields}&offset=0&limit={max_results}"

    # https://api.semanticscholar.org/api-docs/graph
    # https://www.semanticscholar.org/product/api#api-key-form
    # https://api.semanticscholar.org/graph/v1/paper/search?query=domain+adaptation&fields=title,authors,url,abstract,year,citationCount&offset=0&limit=10

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
        root = ET.fromstring(data)
        return root.findall(".//{http://www.w3.org/2005/Atom}entry")
    except Exception as e:
        print(f"Error fetching arXiv data: {e}")
        return []
