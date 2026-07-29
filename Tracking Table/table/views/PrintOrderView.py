from common.views import BasePrintView
from table.models import Order

class PrintOrder(BasePrintView):

    """

    Hierarchy:
    LoginRequiredMixin -> TemplateView -> BasePrintView -> PrintOrder

    --- Fields inherited from BasePrintView ---

    model = None
    template_name = None
    order_context = None

    """

    model = Order
    template_name = 'table/print_order.html'
    order_context = "order"
    