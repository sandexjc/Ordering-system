from common.models import BaseItem
from vitrine.models.base import VitrineItem


class Seal(VitrineItem, BaseItem):

    def __str__(self):
        return f'Seal: {self.quantity} / Vitrine ID: {self.vitrine_id}'