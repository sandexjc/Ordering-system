from common.managers import BaseManager
from table.querysets import TableItemQuerySet


class TableItemManager(BaseManager):

    # Application specific (intermediate level) order related items queryset manager

    def __get_queryset(self):
        return TableItemQuerySet(self.model, using=self._db).active()

    # Return order related active only items
    def for_order(self, order):
        return self.__get_queryset().for_order(order)

    def for_order_id(self, order_id):
        return self.__get_queryset().for_order_id(order_id)