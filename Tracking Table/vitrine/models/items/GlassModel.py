from django.db import models
from django.core.validators import MinValueValidator
from vitrine.models.base import VitrineItem, VitrineFrameItem


class Glass(VitrineItem, VitrineFrameItem):

    """

    Hierarchy:
    BaseModel -> VitrineItem -> Glass
    BaseItem -> VitrineFrameItem -> Glass

    --- Fields inherited from BaseModel via VitrineItem ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    --- Fields inherited from VitrineItem ---

    vitrine_id = models.ForeignKey(Vitrine, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = VitrineItemManager()

    --- Fields inherited from BaseItem via VitrineFrameItem ---

    quantity = models.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(0.49)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    --- Fields inherited from VitrineFrameItem ---

    frame_id = models.ForeignKey(Frame, on_delete=models.CASCADE, related_name="%(class)ss")
    frame_objects = VitrineFrameItemManager()

    """

    glass_type = models.CharField(max_length=50, blank=True, null=True)

    # Override BaseItem quantity field to align with model requirements
    quantity = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.01)])

    def __str__(self):
        return f'Glass: {self.glass_type} / Vitrine ID: {self.vitrine_id}'