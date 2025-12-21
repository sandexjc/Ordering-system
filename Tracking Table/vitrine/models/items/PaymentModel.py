from common.models import BasePayment
from vitrine.service import BaseVitrineItemWorkflow
from vitrine.models.base import VitrineItem


class Payment(VitrineItem, BasePayment):

    # Service layer workflow model speific functionality
    workflow_service_class = BaseVitrineItemWorkflow

    def __str__(self):
        return f'Payment for Vitrine ID: {self.vitrine_id}'