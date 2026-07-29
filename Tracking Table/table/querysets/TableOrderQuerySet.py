from common.querysets import BaseOrderQuerySet

class TableOrderQuerySet(BaseOrderQuerySet):

    """
    Table app domain level shared Order models queryset.

    Hierarchy:
    models.QuerySet
        \
         -> BaseQuerySet -> BaseOrderQuerySet -> TableOrderQuerySet

    --- Fields inherited from BaseOrderQuerySet ---

    No explicit class fields inherited.

    """
    
    # Order type filtering (order/offer)
    def order_type(self, order_type):
        return self.filter(order_type=order_type)