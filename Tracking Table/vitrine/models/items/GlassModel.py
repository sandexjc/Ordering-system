from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import BaseItem
from vitrine.models.base import VitrineItem


class Glass(VitrineItem, BaseItem):

    glass_type = models.CharField(max_length=50)
    quantity = models.IntegerField(default=1, editable=False, validators=[MinValueValidator(1), MaxValueValidator(1)])

    def __str__(self):
        return f'Glass: {self.glass_type} / Vitrine ID: {self.vitrine_id}'