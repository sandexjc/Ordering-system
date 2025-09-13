from common.models import BaseModel
from table.managers import TableOrderManager

class TableOrder(BaseModel):

    objects = TableOrderManager()

    class Meta:
        abstract = True