from django.db import models
from common.models import BaseItem
from table.models.base import TableItem


class Edge(TableItem, BaseItem):

    edge_type = models.CharField(max_length=50)
    color_code = models.CharField(max_length=50, default='')

    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    visible = models.BooleanField(default=True)

    def __str__(self):
        return f'Edge: {self.edge_type} / Order ID: {self.order_id}'