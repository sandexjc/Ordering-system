from common.models import BaseChange
from vitrine.models import VitrineItem

class Change(VitrineItem, BaseChange):

    def __str__(self):
        return f'User: {self.user} / Order ID: {self.vitrine_id}'