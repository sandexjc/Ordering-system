from django.db import models

from common.models import BaseItem
from table.service import BaseTableItemWorkflow
from table.models.base import TableItem


class Edging(TableItem, BaseItem):

    """

    Hierarchy:
    BaseModel -> TableItem -> Edging
    BaseItem -> Edging

    --- Fields inherited from BaseModel via TableItem ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    --- Fields inherited from TableItem ---

    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = TableItemManager()

    --- Fields inherited from BaseItem ---

    quantity = models.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(0.49)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    """

    # Service layer workflow model speific functionality
    workflow_service_class = BaseTableItemWorkflow

    edging_type = models.CharField(max_length=50)

    def __str__(self):
        return f'Edging: {self.edging_type} / Order ID: {self.order_id}'