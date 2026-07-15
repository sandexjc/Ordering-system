from common.views import MainView
from vitrine.models import Vitrine
from django.core.exceptions import ObjectDoesNotExist


class BaseVitrineView(MainView):

    """ Vitrine application domain base view """

    model = Vitrine
    template_name = 'vitrine/vitrines.html'

    def get_queryset_by_search(self, category, search_value):
        if category == 'ID':
            if search_value.isnumeric():
                try:
                    return [self.model.objects.get_by_id(search_value)]
                except ObjectDoesNotExist:
                    return []
            return []

        elif category == 'Telephone':
            return self.model.objects.telephone_contains(self.order_type, search_value)
        elif category == 'Client Name':
            return self.model.objects.owner_contains(self.order_type, search_value)
        elif category == 'All':
            return (
                self.model.objects.telephone_contains(self.order_type, search_value)
                | self.model.objects.owner_contains(self.order_type, search_value)
            )
        return []

    def get_queryset_latest_by_count(self, count):
        return self.model.objects.latest_by_count(self.order_type, count)

    def get_queryset_all(self):
        return self.model.objects.all_by_order_type(self.order_type)

    def get_default_queryset(self):
        return self.model.objects.latest_by_count(self.order_type, self.default_items_count)