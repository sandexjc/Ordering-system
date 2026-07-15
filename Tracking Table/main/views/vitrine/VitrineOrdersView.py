from main.views.base import BaseVitrineView


class VitrineOrders(BaseVitrineView):

    """ Main view for displaying vitrine orders. """

    order_type = "order"
    navigation = "vitrine"
