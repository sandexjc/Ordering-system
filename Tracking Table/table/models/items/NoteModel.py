from django.db import models
from django.utils import timezone
from table.models.base import TableItem

class Note(TableItem):

    user = models.CharField(max_length=50, default='n/a')
    date = models.DateTimeField(default=timezone.now)
    content = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f'{self.user} / Order ID: {self.order_id}'