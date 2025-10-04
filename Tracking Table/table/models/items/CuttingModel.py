from django.db import models
from common.models import BaseItem
from table.models.base import TableItem

class Cutting(TableItem, BaseItem):

    cutting_type = models.CharField(max_length=50)

    def __str__(self):
        return f'Cutting: {self.cutting_type} / Order ID: {self.order_id}'