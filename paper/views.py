from django.shortcuts import render, redirect
from .models import Paper

def paper_list(request):
    papers = Paper.objects.all().order_by("-publish_date")
    return render(request, "paper/paper_list.html", {"papers": papers})

def paper_create(request):
    if request.method == "POST":
        title = request.POST["title"]
        author = request.POST["author"]
        publish_date = request.POST["publish_date"]
        Paper.objects.create(title=title,
                             author=author,
                             publish_date=publish_date)
        return redirect("paper_list")
    return render(request, "paper/paper_create.html")
