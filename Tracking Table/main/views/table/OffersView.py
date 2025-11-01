from main.views.base import BaseTableView

class Offers(BaseTableView):

    # Main view for displaying offers

    clients_type = "External"
    navigation = clients_type