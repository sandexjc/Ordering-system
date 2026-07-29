from django.db import models
from vitrine.models.base import VitrineItem, VitrineFrameItem


class Seal(VitrineItem, VitrineFrameItem):

    """

    Hierarchy:
    BaseModel -> VitrineItem -> Seal
    BaseItem -> VitrineFrameItem -> Seal

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

    seal_types = [
        ('Black', 'Черно'),
        ('White', 'Бяло'),
    ]

    seal_type = models.CharField(choices=seal_types, default='Black', max_length=10)

    def __str__(self):
        return f'Seal: {self.seal_type} / Vitrine ID: {self.vitrine_id}'