from common.managers import BaseManager
from table.querysets import TableOrderQuerySet

class TableOrderManager(BaseManager):
    
    def __get_queryset(self):
        return TableOrderQuerySet(self.model, using=self._db).active()
    
    def __common_filter(self, client_type: str, *related_items):
        return (
            self.__get_queryset()
            .client_type(client_type)
            .last_created()
            .with_items(*related_items)
        )

    # Return signle order with related items by primary key
    def get_by_id(self, id, *related_items):
        return (
            self.__get_queryset()
            .with_items(*related_items)
            .filter(pk=id)
            .first()
        )
    
    #####################################################
    #                                                   #
    #   Below querysets are sharing common logic:       #
    #                                                   #
    #   - 1. Filtered by the given client type.         #
    #   - 2. Results are ordered by -created_date.      #
    #   - 3. Each order is returned with related items. #
    #                                                   #
    #####################################################

    # Return all orders
    def all_by_client_type(self, client_type: str, *related_items):
        return (
            self.__common_filter(client_type, *related_items)
        )
    
    # Return most recently N created orders 
    def latest_by_count(self, client_type: str, count: int=100, *related_items):
        return (
            self.__common_filter(client_type, *related_items)[:count]
        )

    # Return most recently created orders
    def latest_by_date(self, client_type: str, days: int=30, *related_items):
        return (
            self.__common_filter(client_type, *related_items)
            .most_recent(days)
        )

    # Return orders created in given time period
    def created_between(self, client_type: str, start_date, end_date, *related_items):
        return (
            self.__common_filter(client_type, *related_items)
            .created_between(start_date, end_date)
        )

    # Return orders which contains given telephone number
    def telephone_contains(self, client_type: str, number, *related_items):
        return (
            self.__common_filter(client_type, *related_items)
            .telephone_contains(number)
        )

    # Return orders which contains given name
    def owner_contains(self, client_type: str, name, *related_items):
        return (
            self.__common_filter(client_type, *related_items)
            .owner_contains(name)
        )
    