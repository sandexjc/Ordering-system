from django.db import models
from common.models import BaseItem
from vitrine.managers import VitrineFrameItemManager
from vitrine.models.items.FrameModel import Frame

class VitrineFrameItem(BaseItem):

    frame_id = models.ForeignKey(Frame, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = VitrineFrameItemManager()

    class Meta:
        abstract = True