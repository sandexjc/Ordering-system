from django.db import models
from common.models import BaseOrder
from vitrine.models.base import VitrineOrder

class Vitrine(VitrineOrder, BaseOrder):

    """ 

    Fields inheritance from BaseOrder:
    
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    """

    id = models.BigAutoField(primary_key=True)

    # Vitrine related items total values
    frames_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    holes_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    others_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    seals_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    manufacturing_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    
    def __str__(self):
        return str(self.id)