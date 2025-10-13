from django.db import models
from common.models import BaseOrder
from vitrine.models.base import VitrineOrder

class Vitrine(VitrineOrder, BaseOrder):

    id = models.BigAutoField(primary_key=True)

    frame_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    glass_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    holes_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    other_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    seals_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    def __str__(self):
        return str(self.id)