from main.views.base import BaseTableView

class Orders(BaseTableView):

    clients_type = "Internal"
    navigation = clients_type