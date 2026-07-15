from django.db import models
from django.utils import timezone

class BaseOrder(models.Model):

    order_type_choices = [
        ("order", "Поръчка"),
        ("offer", "Оферта"),
    ]

    created_date = models.DateTimeField(default=timezone.now)
    owner = models.CharField(max_length=50)
    telephone = models.CharField(max_length=14, blank=True)

    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    order_ready = models.BooleanField(default=False)
    order_taken = models.BooleanField(default=False)
    order_type = models.CharField(max_length=10, choices=order_type_choices, default="offer")
    
    class Meta:
        abstract = True
