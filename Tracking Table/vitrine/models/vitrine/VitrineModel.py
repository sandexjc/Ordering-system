from django.db import models
from common.models import BaseOrder
from vitrine.models.base import VitrineOrder

class Vitrine(VitrineOrder, BaseOrder):

    id = models.BigAutoField(primary_key=True)

    # Frames totals
    frame_inox_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    frame_black_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    frame_matte_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    frames_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    # Holes totals
    holes_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    # Other services totals
    others_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    # Seals totals
    seal_white_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    seal_black_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    seals_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    # Manufacturing total
    manufacturing_total = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    """ 

    Fields inheritance from BaseOrder:
    
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    """
    
    def __str__(self):
        return str(self.id)