from django.db import models
from vitrine.models.base import VitrineItem, VitrineFrameItem


class Seal(VitrineItem, VitrineFrameItem):

    seal_types = [
        ('Black', 'Черно'),
        ('White', 'Бяло'),
    ]

    seal_type = models.CharField(choices=seal_types, default='Black', max_length=10)

    def __str__(self):
        return f'Seal: {self.seal_type} / Vitrine ID: {self.vitrine_id}'