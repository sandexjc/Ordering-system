from django.db import models

from common.models import BaseItem
from vitrine.managers import VitrineFrameItemManager
from vitrine.service import BaseVitrineItemWorkflow

class VitrineFrameItem(BaseItem):

    """

    Hierarchy:
    BaseItem -> VitrineFrameItem

    --- Fields inherited from BaseItem ---

    quantity = models.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(0.49)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    """

    # Service layer workflow model speific functionality
    workflow_service_class = BaseVitrineItemWorkflow

    frame_id = models.ForeignKey("vitrine.Frame", on_delete=models.CASCADE, related_name="%(class)ss")
    frame_objects = VitrineFrameItemManager()

    class Meta:
        abstract = True