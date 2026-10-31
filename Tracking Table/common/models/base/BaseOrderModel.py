from django.db import models
from django.utils import timezone

class BaseOrder(models.Model):

    """

    Hierarchy:
    models.Model -> BaseOrder

    --- Fields inherited from models.Model ---

    No explicit class fields inherited.

    """

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

    # Id of the create request that inserted this order. A repeated create with this id returns the saved order.
    create_uuid = models.CharField(max_length=36, null=True, blank=True, unique=True)
    
    class Meta:
        abstract = True
