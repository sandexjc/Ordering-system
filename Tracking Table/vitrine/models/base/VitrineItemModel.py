from django.db import models
from common.models import BaseModel
from vitrine.managers import VitrineItemManager
from vitrine.models.vitrine import Vitrine

class VitrineItem(BaseModel):

    vitrine_id = models.ForeignKey(Vitrine, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = VitrineItemManager()

    class Meta:
        abstract = True