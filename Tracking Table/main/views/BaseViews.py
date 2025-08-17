from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from table.models import Order
from main import forms
from common import custom_classes
import time

class OrdersView(LoginRequiredMixin, TemplateView):
    template_name = 'orders.html'

    def search_id(self, ID):
        return Order.objects.filter(ID=ID)

    def search_date(self, date):
        return Order.objects.filter(client=self.clients_type, created_date__contains=date).order_by('-created_date')

    def search_name(self, name):
        return Order.objects.filter(client=self.clients_type, owner__icontains=name).order_by('-created_date')

    def search_telephone(self, telephone):
        return Order.objects.filter(client=self.clients_type, telephone__icontains=telephone).order_by('-created_date')

    def search_all(self, search_kwd):
        return (
            Order.objects.filter(client=self.clients_type, created_date__contains=search_kwd).order_by('-created_date') |
            Order.objects.filter(client=self.clients_type, owner__icontains=search_kwd).order_by('-created_date') |
            Order.objects.filter(client=self.clients_type, telephone__icontains=search_kwd).order_by('-created_date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = []
        context['filter_badge'] = True
        context['nav_select'] = self.clients_type
        
        if self.request.POST:

            if self.request.POST['action'] == 'Search':

                context['filter_form'] = forms.FilterForm
                context['search_form'] = forms.SearchForm(self.request.POST)
                context['category'] = self.request.POST['category']
                context['search_string'] = self.request.POST['search_field']
                context['search_error'] = False

                if self.request.POST['category'] == 'ID':
                    context['search_error'] = True
                    if self.request.POST['search_field'].isnumeric():
                        orders = self.search_id(self.request.POST['search_field'])
                        context['search_error'] = False

                elif self.request.POST['category'] == 'Date':
                    orders = self.search_date(self.request.POST['search_field'])
                elif self.request.POST['category'] == 'Telephone':
                    orders = self.search_telephone(self.request.POST['search_field'])
                elif self.request.POST['category'] == 'Client Name':
                    orders = self.search_name(self.request.POST['search_field'])
                elif self.request.POST['category'] == 'All':
                    orders = self.search_all(self.request.POST['search_field'])

                if len(self.request.POST['search_field']) == 0:
                    context['badges'] = False
                else:
                    context['badges'] = True

            elif self.request.POST['action'] == 'Filter':

                if self.request.POST['fast_select'].isnumeric():
                    orders = Order.objects.filter(client=self.clients_type).order_by('-created_date')[:int(self.request.POST['fast_select'])]
                    context['filter_badge'] = True
                else:
                    orders = Order.objects.filter(client=self.clients_type).order_by('-created_date')
                    context['filter_badge'] = False


                context['search_form'] = forms.SearchForm
                context['filter_form'] = forms.FilterForm(self.request.POST)

        else:
            orders = Order.objects.filter(client=self.clients_type).order_by('created_date')[:100]
            context['search_form'] = forms.SearchForm
            context['filter_form'] = forms.FilterForm
            context['badges'] = False

        context['visible_items'] = len(orders)

        for order in orders:
            context['orders'].append(custom_classes.OrderObject(order))

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