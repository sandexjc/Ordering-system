from django.db import models

from common.models import BaseItem
from vitrine.models.base import VitrineItem
from vitrine.service import OtherWorkflow


class Other(VitrineItem, BaseItem):

    """

    Hierarchy:
    BaseModel -> VitrineItem -> Other
    BaseItem -> Other

    --- Fields inherited from BaseModel via VitrineItem ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    --- Fields inherited from VitrineItem ---

    vitrine_id = models.ForeignKey(Vitrine, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = VitrineItemManager()

    --- Fields inherited from BaseItem ---

    quantity = models.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(0.49)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    """

    # Service layer workflow model speific functionality
    workflow_service_class = OtherWorkflow

    description = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.description} / Vitrine ID: {self.vitrine_id}'