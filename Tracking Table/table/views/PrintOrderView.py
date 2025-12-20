from common.views import BasePrintView
from table.models import Order

class PrintOrder(BasePrintView):
    
    model = Order
    template_name = 'table/print_order.html'
    order_context = "order"
    