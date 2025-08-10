from django.db import models
from django.core.validators import MinValueValidator
from .OrderModel import Order

class Payment(models.Model):

    payment_methods = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Bank', 'Bank'),
    ]

    cutID = models.ForeignKey(Order, on_delete=models.CASCADE)

    value = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.00)])
    payment_method = models.CharField(choices=payment_methods, default='Cash', max_length=10)

    def __str__(self):
        return f'Payment for {self.cutID}'