from common.managers import BaseOrderManager
from table.querysets import TableOrderQuerySet

class TableOrderManager(BaseOrderManager):

    """
    Table app domain level Orders manager.

    Hierarchy:
    models.Manager
        \
         -> BaseManager -> BaseOrderManager -> TableOrderManager

    --- Fields inherited from BaseOrderManager ---

    No explicit class fields inherited.

    """
    
    def __get_queryset(self):
        return TableOrderQuerySet(self.model, using=self._db).active()
    
    def __common_filter(self, order_type: str, *related_items):
        return (
            self.__get_queryset()
            .order_type(order_type)
            .last_created()
            .with_items(*related_items)
        )
    
    
    #####################################################
    #                                                   #
    #   Below querysets are sharing common logic:       #
    #                                                   #
    #   - 1. Filtered by the given order type.          #
    #   - 2. Results are ordered by -created_date.      #
    #   - 3. Each order is returned with related items. #
    #                                                   #
    #####################################################

    # Return all orders
    def all_by_order_type(self, order_type: str, *related_items):
        return (
            self.__common_filter(order_type, *related_items)
        )
    
    # Return most recently N created orders 
    def latest_by_count(self, order_type: str, count: int=100, *related_items):
        return (
            self.__common_filter(order_type, *related_items)[:count]
        )

    # Return most recently created orders
    def latest_by_date(self, order_type: str, days: int=30, *related_items):
        return (
            self.__common_filter(order_type, *related_items)
            .most_recent(days)
        )

    # Return orders created in given time period
    def created_between(self, order_type: str, start_date, end_date, *related_items):
        return (
            self.__common_filter(order_type, *related_items)
            .created_between(start_date, end_date)
        )

    # Return orders which contains given telephone number
    def telephone_contains(self, order_type: str, number, *related_items):
        return (
            self.__common_filter(order_type, *related_items)
            .telephone_contains(number)
        )

    # Return orders which contains given name
    def owner_contains(self, order_type: str, name, *related_items):
        return (
            self.__common_filter(order_type, *related_items)
            .owner_contains(name)
        )
    