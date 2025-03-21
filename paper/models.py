from django.db import models
from topic.models import Topic


class Paper(models.Model):
    title = models.CharField(max_length=256)
    author = models.CharField(max_length=80)
    publisher = models.CharField(max_length=80, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    doi = models.CharField(max_length=80, blank=True)
    url = models.URLField(max_length=1024)
    pdf_url = models.URLField(max_length=1024)
    pdf_name = models.CharField(max_length=255, blank=True)
    citations = models.IntegerField(default=0)
    tags = models.CharField(max_length=256, blank=True)
    update_date = models.DateTimeField(auto_now=True)
    note = models.TextField(blank=True)
    annotation = models.TextField(blank=True)
    topics = models.ManyToManyField(Topic, related_name="papers")

    def __str__(self):
        if self.publish_date:
            return f'{self.author}, "{self.title}," {self.publisher}, {self.publish_date.strftime("%Y")}.'
        else:
            return f'{self.author}, "{self.title}," {self.publisher}.'
