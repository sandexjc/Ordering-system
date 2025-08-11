from common.views import OrdersView

class InternalsView(OrdersView):
    def __init__(self):
        super().__init__()
        self.clients_type = 'Internal'