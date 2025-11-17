from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import BaseItem
from vitrine.models.base import VitrineItem


class Frame(VitrineItem, BaseItem):

    profile_types = [
        ('Black', 'Черен'),
        ('Matte', 'Мат'),
        ('Inox', 'Инокс'),
    ]

    profile_type = models.CharField(choices=profile_types, default='Black', max_length=10)
    length = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20000)], default=0)
    width = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20000)], default=0)

    # Override BaseItem quantity field to align with model requirements
    quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(99)], default=1)

    def __str__(self):
        return f"Frame color: {self.profile_type} / Vitrine ID: {self.vitrine_id}"