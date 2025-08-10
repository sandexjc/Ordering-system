from django.db import models
from django.utils import timezone
from .OrderModel import Order

class Note(models.Model):

    cutID = models.ForeignKey(Order, on_delete=models.CASCADE)

    user = models.CharField(max_length=50, default='n/a')
    date = models.DateTimeField(default=timezone.now)
    content = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f'{self.user} - {self.content}'