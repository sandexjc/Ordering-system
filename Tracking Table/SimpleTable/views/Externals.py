from SimpleTable.views.BaseViews import OrdersView

class ExternalsView(OrdersView):
    def __init__(self):
        super().__init__()
        self.clients_type = 'External'