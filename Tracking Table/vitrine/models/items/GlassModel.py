from django.db import models
from vitrine.models.base import VitrineItem, VitrineFrameItem


class Glass(VitrineItem, VitrineFrameItem):

    glass_type = models.CharField(max_length=50)

    def __str__(self):
        return f'Glass: {self.glass_type} / Vitrine ID: {self.vitrine_id}'