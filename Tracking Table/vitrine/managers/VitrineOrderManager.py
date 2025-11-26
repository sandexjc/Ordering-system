from common.managers import BaseOrderManager
from vitrine.querysets import VitrineOrderQuerySet

class VitrineOrderManager(BaseOrderManager):

    """ Vitrine app domain level manager. """
    
    def __get_queryset(self):
        return VitrineOrderQuerySet(self.model, using=self._db).active()
    
    def __common_filter(self, *related_items):
        return (
            self.__get_queryset()
            .last_created()
            .with_items(*related_items)
        )
    
    # Return most recently N created orders 
    def latest_by_count(self, count: int=100, *related_items):
        return (
            self.__common_filter(*related_items)[:count]
        )
    
    # Return most recently created orders
    def latest_by_date(self, days: int=30, *related_items):
        return (
            self.__common_filter(*related_items)
            .most_recent(days)
        )
    
    # Return orders created in given time period
    def created_between(self, start_date, end_date, *related_items):
        return (
            self.__common_filter(*related_items)
            .created_between(start_date, end_date)
        )

    # Return orders which contains given telephone number
    def telephone_contains(self, number, *related_items):
        return (
            self.__common_filter(*related_items)
            .telephone_contains(number)
        )

    # Return orders which contains given name
    def owner_contains(self, name, *related_items):
        return (
            self.__common_filter(*related_items)
            .owner_contains(name)
        )