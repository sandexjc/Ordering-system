from main.views.base import BaseTableView


class TableOrders(BaseTableView):

    """
    Main view for displaying table orders.

    Hierarchy:
    LoginRequiredMixin
            \
             -> MainView -> BaseTableView -> TableOrders
            /
    TemplateView

    --- Fields inherited from BaseTableView ---

    model = Order
    template_name = "table/orders.html"

    """

    order_type = "order"
    navigation = "table"
