from django.db import models

from vitrine.service import OtherWorkflow
from common.models import BaseItem
from vitrine.models.base import VitrineItem


class Other(VitrineItem, BaseItem):

    # Service layer workflow model speific functionality
    workflow_service_class = OtherWorkflow

    description = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.description} / Vitrine ID: {self.vitrine_id}'