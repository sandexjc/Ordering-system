from django.db import models
from django.utils import timezone

class BaseOrder(models.Model):

    created_date = models.DateTimeField(default=timezone.now)
    owner = models.CharField(max_length=50)
    telephone = models.CharField(max_length=14, blank=True)

    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    order_ready = models.BooleanField(default=False)
    order_taken = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
