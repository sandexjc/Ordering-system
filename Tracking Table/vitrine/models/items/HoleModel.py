from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import BaseItem
from vitrine.models.base import VitrineItem


class Hole(VitrineItem, BaseItem):

    directions = [
        ('down', 'отдолу'),
        ('up', 'отгоре'),
    ]

    positions = [
        ('left', 'лява'),
        ('right', 'дясна'),
    ]

    direction = models.CharField(choices=directions, default='down', max_length=10)
    position_x = models.CharField(choices=positions, default='right', max_length=10)
    position_y = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20000)], default=0)
    quantity = models.IntegerField(default=1, editable=False, validators=[MinValueValidator(1), MaxValueValidator(1)])

    def __str__(self):
        return f"Hole: {self.id} / Vitrine ID: {self.vitrine_id}"