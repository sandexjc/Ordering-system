from common.models import BasePayment
from table.models.base import TableItem


class Payment(TableItem, BasePayment):

    def __str__(self):
        return f'Payment: {self.value} / Order ID: {self.order_id}'