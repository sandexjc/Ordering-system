from .BaseManager import BaseManager
from common.querysets import BaseOrderQuerySet

class BaseOrderManager(BaseManager):

    """ Queryset Manager designed to share common Order models logic between apps. """

    def __get_queryset(self):
        return BaseOrderQuerySet(self.model, using=self._db).active()

    # Return signle order with related items by primary key
    def get_by_id(self, id, *related_items):
        return (
            self.__get_queryset()
            .with_items(*related_items)
            .filter(pk=id)
            .first()
        )

