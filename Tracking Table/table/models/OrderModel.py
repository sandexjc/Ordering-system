from django.db import models
from django.utils import timezone
from .TableOrderModel import TableOrder

class Order(TableOrder):

    client_statuses = [
        ('Internal', 'Internal'),
        ('External', 'External'),
    ]

    id = models.BigAutoField(primary_key=True)
    created_date = models.DateTimeField(default=timezone.now)
    owner = models.CharField(max_length=50)
    client = models.CharField(choices=client_statuses, default='Internal', max_length=50)
    telephone = models.CharField(max_length=14, blank=True)

    plates_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    edge_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cutting_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    edging_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    others_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    order_ready = models.BooleanField(default=False)
    order_taken = models.BooleanField(default=False)

    invoice = models.BooleanField(default=False)

    def clear(self):

        self.plates_total = 0
        self.edge_total = 0
        self.cutting_total = 0
        self.edging_total = 0
        self.others_total = 0
        self.paid = 0
        self.total_price = 0

    def __str__(self):
        return str(self.id)