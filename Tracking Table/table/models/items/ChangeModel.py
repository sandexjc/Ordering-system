from common.models import BaseChange
from table.models import TableItem

class Change(TableItem, BaseChange):

    def __str__(self):
        return f'User: {self.user} / Order ID: {self.order_id}'