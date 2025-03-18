from django.db import models
import uuid


class Paper(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=256)
    author = models.TextField(max_length=80)
    publisher = models.TextField(max_length=80)
    publish_date = models.DateTimeField()
    doi = models.TextField(max_length=80)
    url = models.TextField(max_length=1024)
    pdf_url = models.TextField(max_length=1024)
    pdf_name = models.TextField(max_length=1024)
    citations = models.IntegerField(default=0)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.author + ', ' + self.title + ', ' + self.publish_date.strftime('%Y.')
