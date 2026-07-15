from common.querysets import BaseOrderQuerySet

class VitrineOrderQuerySet(BaseOrderQuerySet):

    """ Vitrine app domain level shared Vitrine models queryset. """

    def order_type(self, order_type):
        return self.filter(order_type=order_type)