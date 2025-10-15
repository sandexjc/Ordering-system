from django.db import models
from common.models import BaseOrder
from table.models.base import TableOrder

class Order(TableOrder, BaseOrder):

    client_statuses = [
        ('Internal', 'Поръчка'),
        ('External', 'Оферта'),
    ]

    id = models.BigAutoField(primary_key=True)
    client = models.CharField(choices=client_statuses, default='External', max_length=50)

    plates_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    edge_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cutting_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    edging_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    others_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

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