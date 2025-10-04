from django.db import models
from common.models import BaseItem
from table.models.base import TableItem


class Other(TableItem, BaseItem):

    description = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.description} / Order ID: {self.order_id}'