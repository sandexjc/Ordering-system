from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from table.models import Order
from main.forms import SearchForm, FilterForm
import time

DEFAULT_ORDERS_COUNT = 100

class OrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'orders.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_badge'] = True
        context['nav_select'] = self.clients_type
        
        if self.request.POST:

            if self.request.POST['action'] == 'Search':

                context['filter_form'] = FilterForm
                context['search_form'] = SearchForm(self.request.POST)
                context['category'] = self.request.POST['category']
                context['search_string'] = self.request.POST['search_field']
                context['search_error'] = False

                if self.request.POST['category'] == 'ID':
                    context['search_error'] = True
                    if self.request.POST['search_field'].isnumeric():
                        context['orders'] = [Order.objects.get_by_id(self.request.POST['search_field'])]
                        context['search_error'] = False

                elif self.request.POST['category'] == 'Telephone':
                    context['orders'] = Order.objects.telephone_contains(self.clients_type, self.request.POST['search_field'])
                elif self.request.POST['category'] == 'Client Name':
                    context['orders'] = Order.objects.owner_contains(self.clients_type, self.request.POST['search_field'])
                elif self.request.POST['category'] == 'All':
                    context['orders'] = (
                        Order.objects.telephone_contains(self.clients_type, self.request.POST['search_field']) |
                        Order.objects.owner_contains(self.clients_type, self.request.POST['search_field'])
                    )
                    
                if len(self.request.POST['search_field']) == 0:
                    context['badges'] = False
                else:
                    context['badges'] = True

            elif self.request.POST['action'] == 'Filter':

                if self.request.POST['fast_select'].isnumeric():
                    context['orders'] = Order.objects.latest_by_count(self.clients_type, int(self.request.POST['fast_select']))
                    context['filter_badge'] = True
                else:
                    context['orders'] = Order.objects.all_by_client_type(self.clients_type)
                    context['filter_badge'] = False


                context['search_form'] = SearchForm
                context['filter_form'] = FilterForm(self.request.POST)

        else:
            context['orders'] = Order.objects.latest_by_count(self.clients_type, DEFAULT_ORDERS_COUNT)
            context['search_form'] = SearchForm
            context['filter_form'] = FilterForm
            context['badges'] = False

        context['visible_items'] = len(context['orders'])
        current_time = time.localtime(time.time())

        if current_time.tm_hour in range(7, 10):
            context['current_time'] = 'Morning'
        elif current_time.tm_hour in range(11, 15):
            context['current_time'] = 'Day'
        elif current_time.tm_hour in range(16, 19):
            context['current_time'] = 'Afternoon'
        else:
            context['current_time'] = 'Night'

        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())