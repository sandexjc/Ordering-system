from django.db import models
from django.core.validators import MinValueValidator
from vitrine.models.base import VitrineItem, VitrineFrameItem


class Glass(VitrineItem, VitrineFrameItem):

    glass_type = models.CharField(max_length=50)

    # Override BaseItem quantity field to align with model requirements
    quantity = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f'Glass: {self.glass_type} / Vitrine ID: {self.vitrine_id}'