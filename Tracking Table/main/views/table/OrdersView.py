from main.views.base import BaseTableView

class Orders(BaseTableView):

    # Main view for displaying placed orders

    clients_type = "Internal"
    navigation = clients_type