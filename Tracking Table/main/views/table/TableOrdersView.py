from main.views.base import StaticView
from table.models import Order


class TableOrders(StaticView):

    """
    Main view for displaying table orders.

    Hierarchy:
    LoginRequiredMixin
            \
             -> MainView -> StaticView -> TableOrders
            /
    TemplateView

    --- Fields inherited from StaticView ---

    model = Order
    template_name = "table/orders.html"

    """

    model = Order
    template_name = "table/orders.html"
    order_type = "order"
    navigation = "table"
