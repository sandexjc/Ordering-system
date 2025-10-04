from django.db import models
from common.models import BaseItem
from table.models.base import TableItem


class Edging(TableItem, BaseItem):

    edging_type = models.CharField(max_length=50)

    def __str__(self):
        return f'Edging: {self.edging_type} / Order ID: {self.order_id}'