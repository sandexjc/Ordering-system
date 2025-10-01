from django.db import models
from django.core.validators import MinValueValidator
from table.models.base import TableItem

class Edging(TableItem):

    edging_type = models.CharField(max_length=50)
    quantity = models.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(0.49)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.edging_type} / Order ID: {self.order_id}'