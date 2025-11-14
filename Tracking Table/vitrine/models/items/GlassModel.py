from django.db import models
from common.models import BaseItem
from vitrine.models.base import VitrineItem
from .FrameModel import Frame


class Glass(VitrineItem, BaseItem):

    glass_type = models.CharField(max_length=50)
    frame_id = models.ForeignKey(Frame, on_delete=models.CASCADE, related_name="%(class)ss")

    def __str__(self):
        return f'Glass: {self.glass_type} / Vitrine ID: {self.vitrine_id}'