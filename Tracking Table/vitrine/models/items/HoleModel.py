from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from vitrine.models.base import VitrineItem, VitrineFrameItem


class Hole(VitrineItem, VitrineFrameItem):

    """

    Scheme:
    BaseItem -> VitrineFrameItem -> Hole
    BaseModel -> VitrineItem -> Hole

    Fields inheritance from BaseItem:

     - quantity = models.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(0.49)])
     - price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
     - value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    Fields inheritance from VitrineFrameItem:

     - frame_id = models.ForeignKey(Frame, on_delete=models.CASCADE, related_name="%(class)ss")
     - frame_objects = VitrineFrameItemManager()

    Fields inheritance from VitrineItem:

     - vitrine_id = models.ForeignKey(Vitrine, on_delete=models.CASCADE, related_name="%(class)ss")
     - objects = VitrineItemManager()

    """

    holes_positions = [
        ('length', 'дължина'),
        ('width', 'широчина'),
    ]

    holes_position = models.CharField(choices=holes_positions, default='length', max_length=10)

    # Override BaseItem quantity field to align with model requirements
    quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(99)], default=0)

    def __str__(self):
        return f"Hole: {self.id} / Vitrine ID: {self.vitrine_id}"