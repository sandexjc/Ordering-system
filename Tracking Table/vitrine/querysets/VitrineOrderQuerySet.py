from common.querysets import BaseOrderQuerySet

class VitrineOrderQuerySet(BaseOrderQuerySet):

    """
    Vitrine app domain level shared Vitrine models queryset.

    Hierarchy:
    models.QuerySet
        \
         -> BaseQuerySet -> BaseOrderQuerySet -> VitrineOrderQuerySet

    --- Fields inherited from BaseOrderQuerySet ---

    No explicit class fields inherited.

    """

    def order_type(self, order_type):
        return self.filter(order_type=order_type)