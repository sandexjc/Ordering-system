from django.db import models
from django.utils import timezone


class BaseNote(models.Model):

    user = models.CharField(max_length=50, default='n/a')
    date = models.DateTimeField(default=timezone.now)
    content = models.TextField(max_length=500, blank=True)

    class Meta:
        abstract = True