from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import BaseItem
from vitrine.models.base import VitrineItem


class Frame(VitrineItem, BaseItem):

    """

    Fields inheritance from BaeItem:

    quantity = models.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(0.49)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    Fields inheritance from VitrineItem:

    vitrine_id = models.ForeignKey(Vitrine, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = VitrineItemManager()

    """

    profile_types = [
        ('Black', 'Черен'),
        ('Matte', 'Мат'),
        ('Inox', 'Инокс'),
    ]

    holes_positions = [
        ('length', 'дължина'),
        ('width', 'широчина'),
    ]

    profile_type = models.CharField(choices=profile_types, default='Black', max_length=10)
    length = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20000)], default=0)
    width = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(20000)], default=0)

    # Override BaseItem quantity field to align with model requirements
    quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(99)], default=1)

    # Helper fields for easier handling Frame related items
    holes_count = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(99)], default=0)
    holes_position = models.CharField(choices=holes_positions, default="length", max_length=10)
    glass_type = models.CharField(null=True, blank=True, max_length=10)

    def __str__(self):
        return f"Frame color: {self.profile_type} / Vitrine ID: {self.vitrine_id}"