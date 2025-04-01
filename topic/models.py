from django.db import models


class Topic(models.Model):
    title = models.CharField(max_length=256, blank=False, null=False, unique=True)
    keywords = models.TextField(max_length=256, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} ({self.keywords})' if self.keywords else self.title
