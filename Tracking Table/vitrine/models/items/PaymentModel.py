from common.models import BasePayment
from vitrine.models.base import VitrineItem


class Payment(VitrineItem, BasePayment):

    def __str__(self):
        return f'Payment for Vitrine ID: {self.vitrine_id}'