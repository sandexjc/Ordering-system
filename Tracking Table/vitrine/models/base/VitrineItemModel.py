from django.db import models
from common.models import BaseModel
from vitrine.managers import VitrineItemManager
from vitrine.models.vitrine import Vitrine

class VitrineItem(BaseModel):

    """

    Hierarchy:
    BaseModel -> VitrineItem

    --- Fields inherited from BaseModel ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    """

    vitrine_id = models.ForeignKey(Vitrine, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = VitrineItemManager()

    class Meta:
        abstract = True