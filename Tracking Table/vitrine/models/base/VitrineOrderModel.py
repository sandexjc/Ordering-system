from common.models import BaseModel
from vitrine.managers import VitrineOrderManager

class VitrineOrder(BaseModel):

    objects = VitrineOrderManager()

    class Meta:
        abstract = True