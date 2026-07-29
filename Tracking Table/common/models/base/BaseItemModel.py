from django.db import models
from django.core.validators import MinValueValidator

class BaseItem(models.Model):

    """

    Hierarchy:
    models.Model -> BaseItem

    --- Fields inherited from models.Model ---

    No explicit class fields inherited.

    """

    quantity = models.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(0.49)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        abstract = True