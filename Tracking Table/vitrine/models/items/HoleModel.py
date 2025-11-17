from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from vitrine.models.base import VitrineItem, VitrineFrameItem


class Hole(VitrineItem, VitrineFrameItem):

    holes_positions = [
        ('length', 'дължина'),
        ('width', 'широчина'),
    ]

    holes_position = models.CharField(choices=holes_positions, default='length', max_length=10)

    # Override BaseItem quantity field to align with model requirements
    quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(99)], default=0)

    def __str__(self):
        return f"Hole: {self.id} / Vitrine ID: {self.vitrine_id}"