from django.shortcuts import render, redirect, get_object_or_404
from .models import Topic
from paper.models import Paper


def topic_list(request):
    topics = Topic.objects.all().order_by("title")
    return render(request, "topic/topic_list.html", {"topics": topics})


def topic_create(request):
    if request.method == "POST":
        title = request.POST["title"]
        keywords = request.POST["keywords"]
        Topic.objects.create(title=title, keywords=keywords)
        return redirect("topic_list")
    return render(request, "topic/topic_create.html")


def topic_detail(request, id):
    topic = get_object_or_404(Topic, id=id)
    papers = Paper.objects.filter(topics=topic).order_by("-publish_date")

    return render(
        request, "topic/topic_detail.html", {"topic": topic, "papers": papers}
    )


def topic_update(request, id):
    topic = get_object_or_404(Topic, id=id)

    if request.method == "POST":
        title = request.POST["title"]
        keywords = request.POST["keywords"]

        topic = get_object_or_404(Topic, id=id)
        topic.title = title
        topic.keywords = keywords
        topic.save()

    return redirect("topic_list")


def topic_delete(request, id):
    topic = get_object_or_404(Topic, id=id)

    if request.method == "POST":
        topic.delete()

    return redirect("topic_list")
