from django.db import models
from django.core.validators import MinValueValidator
from .TableItemModel import TableItem
from .OrderModel import Order

class Plate(TableItem):

    manufacturers = [
        ('Egger', 'Egger'),
        ('Kronospan', 'Kronospan'),
        ('Other', 'Other'),
    ]
    
    manufacturer = models.CharField(choices=manufacturers, default='Egger', max_length=10)
    material = models.CharField(max_length=50)
    quantity = models.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(0.49)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    from_client = models.BooleanField(default=False)

    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    cutted = models.BooleanField(default=False)
    edged = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.material} / Order ID: {self.order_id}'