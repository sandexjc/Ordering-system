from common.models import BasePayment
from table.service import PaymentWorkflow
from table.models.base import TableItem


class Payment(TableItem, BasePayment):

    # Service layer workflow model speific functionality
    workflow_service_class = PaymentWorkflow

    def __str__(self):
        return f'Payment: {self.value} / Order ID: {self.order_id}'