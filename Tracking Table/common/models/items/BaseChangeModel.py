from django.db import models
from django.utils import timezone

class BaseChange(models.Model):

    date = models.DateTimeField(default=timezone.now)
    user = models.CharField(max_length=100, default='N/A')
    operation = models.CharField(max_length=100, default='N/A')
    what = models.CharField(max_length=100, default='N/A')
    current_state = models.CharField(max_length=100, default='')
    new_state = models.CharField(max_length=100, default='')

    class Meta:
        abstract = True