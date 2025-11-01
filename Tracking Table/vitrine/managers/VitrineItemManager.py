from common.managers import BaseItemManager
from vitrine.querysets import VitrineItemQuerySet


class VitrineItemManager(BaseItemManager):

    """ Vitrine app domain level order related items ( FK ) queryset manager. """

    def __get_queryset(self):
        return VitrineItemQuerySet(self.model, using=self._db).active()

    # Return order related active only items by class
    def for_order(self, order):
        return self.__get_queryset().for_vitrine(order)

    # Return order related active only items by id
    def for_order_id(self, order_id):
        return self.__get_queryset().for_vitrine_id(order_id)

