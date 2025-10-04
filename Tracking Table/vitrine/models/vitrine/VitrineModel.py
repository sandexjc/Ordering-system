from django.db import models
from common.models import BaseOrder
from vitrine.models.base import VitrineOrder

class Vitrine(VitrineOrder, BaseOrder):

    id = models.BigAutoField(primary_key=True)

    
    def __str__(self):
        return str(self.id)