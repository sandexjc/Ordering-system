from common.models import BaseNote
from vitrine.models import VitrineItem


class Note(VitrineItem, BaseNote):

    def __str__(self):
        return f'User: {self.user} / Vitrine ID: {self.vitrine_id}'