from django.db import models
from common.models import BaseModel
from table.models import Order

class TableItem(BaseModel):

    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        abstract = True