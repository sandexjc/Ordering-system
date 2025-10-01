from django.db import models
from django.utils import timezone
from table.models.base import TableItem

class Change(TableItem):

    date = models.DateTimeField(default=timezone.now)
    user = models.CharField(max_length=100, default='N/A')
    operation = models.CharField(max_length=100, default='N/A')
    what = models.CharField(max_length=100, default='N/A')
    current_state = models.CharField(max_length=100, default='')
    new_state = models.CharField(max_length=100, default='')

    def __str__(self):
        return f'Order ID: {self.order_id} - {self.user} {self.operation} {self.what} {self.current_state} {self.new_state}'