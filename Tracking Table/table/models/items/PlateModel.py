from django.db import models

from common.models import BaseItem
from table.service import BaseTableItemWorkflow
from table.models.base import TableItem


class Plate(TableItem, BaseItem):

    """

    Hierarchy:
    BaseModel -> TableItem -> Plate
    BaseItem -> Plate

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

    manufacturers = [
        ('Egger', 'Egger'),
        ('Kronospan', 'Kronospan'),
        ('Other', 'Other'),
    ]
    
    manufacturer = models.CharField(choices=manufacturers, default='Egger', max_length=10)
    material = models.CharField(max_length=50)
    
    from_client = models.BooleanField(default=False)

    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    cutted = models.BooleanField(default=False)
    edged = models.BooleanField(default=False)

    def __str__(self):
        return f'Plate: {self.material} / Order ID: {self.order_id}'