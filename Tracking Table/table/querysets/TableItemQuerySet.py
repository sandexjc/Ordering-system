from common.querysets import BaseItemQuerySet

class TableItemQuerySet(BaseItemQuerySet):

    """ Table app domain level queryset sharing common order related ( FK ) models logic. """
    
    # Get order specific items by class
    def for_order(self, order):
        return self.filter(order_id=order)

    # Get order specific items by id 
    def for_order_id(self, order_id):
        return self.filter(order_id=order_id)