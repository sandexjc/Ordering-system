from django.db import models

from common.models import BaseItem
from table.service import BaseTableItemWorkflow
from table.models.base import TableItem


class Plate(TableItem, BaseItem):

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