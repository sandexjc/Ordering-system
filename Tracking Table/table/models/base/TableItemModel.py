from django.db import models
from common.models import BaseModel
from table.managers import TableItemManager
from table.models.order import Order

class TableItem(BaseModel):

    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = TableItemManager()

    class Meta:
        abstract = True