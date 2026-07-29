from django.db import models
from common.models import BaseModel
from table.managers import TableItemManager
from table.models.order import Order

class TableItem(BaseModel):

    """

    Hierarchy:
    BaseModel -> TableItem

    --- Fields inherited from BaseModel ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = BaseManager()

    """

    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = TableItemManager()

    class Meta:
        abstract = True