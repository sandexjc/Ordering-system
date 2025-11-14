from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import BaseItem
from vitrine.models.base import VitrineItem
from .FrameModel import Frame


class Hole(VitrineItem, BaseItem):

    holes_positions = [
        ('length', 'дължина'),
        ('width', 'широчина'),
    ]

    holes_position = models.CharField(choices=holes_positions, default='length', max_length=10)
    frame_id = models.ForeignKey(Frame, on_delete=models.CASCADE, related_name="%(class)ss")

    def __str__(self):
        return f"Hole: {self.id} / Vitrine ID: {self.vitrine_id}"