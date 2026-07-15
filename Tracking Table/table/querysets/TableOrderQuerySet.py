from common.querysets import BaseOrderQuerySet

class TableOrderQuerySet(BaseOrderQuerySet):

    """ Table app domain level shared Order models queryset. """
    
    # Order type filtering (order/offer)
    def order_type(self, order_type):
        return self.filter(order_type=order_type)