from common.models import BaseNote
from table.models import TableItem


class Note(TableItem, BaseNote):

    def __str__(self):
        return f'User: {self.user} / Order ID: {self.order_id}'