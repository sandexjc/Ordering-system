from common.querysets import BaseQuerySet


class TableItemQuerySet(BaseQuerySet):

    # Application specific (intermediate level) Queryset 
    # that shares common logic between different application models
    
    # Get order specific items
    def for_order(self, order):
        return self.filter(order_id=order)

    def for_order_id(self, order_id):
        return self.filter(order_id=order_id)