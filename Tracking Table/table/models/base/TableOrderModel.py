from common.models import BaseModel
from table.managers import TableOrderManager

class TableOrder(BaseModel):

    """

    Hierarchy:
    BaseModel -> TableOrder

    --- Fields inherited from BaseModel ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    objects = BaseManager()

    """

    objects = TableOrderManager()

    class Meta:
        abstract = True