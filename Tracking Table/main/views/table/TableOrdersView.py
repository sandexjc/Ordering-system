from main.views.base import BaseTableView


class TableOrders(BaseTableView):

    """ Main view for displaying table orders. """

    order_type = "order"
    navigation = "table"
