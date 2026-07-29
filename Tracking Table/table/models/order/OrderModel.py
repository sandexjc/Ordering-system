from django.db import models
from common.models import BaseOrder
from table.models.base import TableOrder

class Order(TableOrder, BaseOrder):

    """

    Hierarchy:
    BaseModel -> TableOrder -> Order
    BaseOrder -> Order

    --- Fields inherited from BaseModel via TableOrder ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    --- Fields inherited from TableOrder ---

    objects = TableOrderManager()

    --- Fields inherited from BaseOrder ---

    created_date = models.DateTimeField(default=timezone.now)
    owner = models.CharField(max_length=50)
    telephone = models.CharField(max_length=14, blank=True)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    order_ready = models.BooleanField(default=False)
    order_taken = models.BooleanField(default=False)
    order_type = models.CharField(max_length=10, choices=order_type_choices, default="offer")

    """

    id = models.BigAutoField(primary_key=True)

    plates_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    edge_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cutting_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    edging_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    others_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    invoice = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)