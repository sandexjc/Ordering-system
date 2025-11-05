from common.views import MainView
from table.models import Order
from django.core.exceptions import ObjectDoesNotExist


class BaseTableView(MainView):

    """ Table application specific base view """

    model = Order
    template_name = 'table/orders.html'

    def get_queryset_by_search(self, category, search_value):
        if category == 'ID':
            if search_value.isnumeric():
                try:
                    return [self.model.objects.get_by_id(search_value)]
                except ObjectDoesNotExist:
                    return []
            return []

        elif category == 'Telephone':
            return self.model.objects.telephone_contains(self.clients_type, search_value)
        elif category == 'Client Name':
            return self.model.objects.owner_contains(self.clients_type, search_value)
        elif category == 'All':
            return (
                self.model.objects.telephone_contains(self.clients_type, search_value)
                | self.model.objects.owner_contains(self.clients_type, search_value)
            )
        return []

    def get_queryset_latest_by_count(self, count):
        return self.model.objects.latest_by_count(self.clients_type, count)

    def get_queryset_all(self):
        return self.model.objects.all_by_client_type(self.clients_type)

    def get_default_queryset(self):
        return self.model.objects.latest_by_count(self.clients_type, self.default_items_count)