from django.core.validators import MinValueValidator
from django.db import models

from common.models import BaseModel
from vitrine.managers import VitrinePriceConfigManager


class VitrinePriceConfig(BaseModel):
    # Fixed key guarantees one active global row for pricing.
    singleton_key = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)

    # Stored in EUR; converted per order currency when copied into new orders.
    black_profile_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0.00)],
    )
    matte_profile_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0.00)],
    )
    inox_profile_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0.00)],
    )
    white_seal_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0.00)],
    )
    black_seal_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0.00)],
    )
    add_hole_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0.00)],
    )
    manufacturing_price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0.00)],
    )

    objects = VitrinePriceConfigManager()

    def save(self, *args, **kwargs):
        self.singleton_key = 1
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Vitrine pricing configuration (EUR)"
