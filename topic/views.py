from django.shortcuts import render, redirect
from .models import Topic

def topic_list(request):
    topics = Topic.objects.all().order_by("title")
    return render(request, "topic/topic_list.html", {"topics": topics})

def topic_create(request):
    if request.method == "POST":
        title = request.POST["title"]
        keywords = request.POST["keywords"]
        Topic.objects.create(title=title,
                             keywords=keywords)
        return redirect("topic_list")
    return render(request, "topic/topic_create.html")
