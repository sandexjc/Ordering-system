from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core import serializers
import json

from table.models import Order, Plate, Edge, Payment, Note, Other
from SimpleTable import forms
import time
import table
from lib import custom_classes

class Internals(LoginRequiredMixin, TemplateView):
    template_name = 'orders.html'

    def get_context_data(self, **kwargs):
        context = super(Internals, self).get_context_data(**kwargs)
        context['orders'] = []
        context['filter_badge'] = True
        context['nav_select'] = 'internals'
        
        if self.request.POST:

            if self.request.POST['action'] == 'Search':

                context['filter_form'] = forms.FilterForm
                context['search_form'] = forms.SearchForm(self.request.POST)

                context['category'] = self.request.POST['category']
                context['search_string'] = self.request.POST['search_field']
                context['search_error'] = False

                results = []
                all_internals = []

                if self.request.POST['category'] == 'ID':
                    context['search_error'] = True
                    if self.request.POST['search_field'].isnumeric():
                        all_internals = search_id('Internal', self.request.POST['search_field'])
                        context['search_error'] = False

                elif self.request.POST['category'] == 'Date':
                    all_internals = search_date('Internal', self.request.POST['search_field'])
                elif self.request.POST['category'] == 'Telephone':
                    all_internals = search_telephone('Internal', self.request.POST['search_field'])
                elif self.request.POST['category'] == 'Client Name':
                    all_internals = search_name('Internal', self.request.POST['search_field'])
                elif self.request.POST['category'] == 'All':
                    all_internals = search_all('Internal', self.request.POST['search_field'])

                if len(self.request.POST['search_field']) == 0:
                    context['badges'] = False
                else:
                    context['badges'] = True

            elif self.request.POST['action'] == 'Filter':

                if self.request.POST['fast_select'].isnumeric():
                    all_internals = Order.objects.filter(client='Internal').order_by('-created_date')[:int(self.request.POST['fast_select'])]
                    context['filter_badge'] = True
                else:
                    all_internals = Order.objects.filter(client='Internal').order_by('-created_date')
                    context['filter_badge'] = False


                context['search_form'] = forms.SearchForm
                context['filter_form'] = forms.FilterForm(self.request.POST)

        else:
            all_internals = Order.objects.filter(client='Internal').order_by('-created_date')[:100]
            context['search_form'] = forms.SearchForm
            context['filter_form'] = forms.FilterForm
            context['badges'] = False

        context['visible_items'] = len(all_internals)

        for internal in all_internals:
            context['orders'].append(custom_classes.OrderObject(internal))

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

class Externals(LoginRequiredMixin, TemplateView):
    template_name = 'orders.html'

    def get_context_data(self, **kwargs):
        context = super(Externals, self).get_context_data(**kwargs)
        context['orders'] = []
        context['filter_badge'] = True
        context['nav_select'] = 'externals'
        
        if self.request.POST:

            if self.request.POST['action'] == 'Search':

                context['filter_form'] = forms.FilterForm
                context['search_form'] = forms.SearchForm(self.request.POST)

                context['category'] = self.request.POST['category']
                context['search_string'] = self.request.POST['search_field']
                context['search_error'] = False

                results = []
                all_externals = []

                if self.request.POST['category'] == 'ID':
                    context['search_error'] = True
                    if self.request.POST['search_field'].isnumeric():
                        all_externals = search_id('External', self.request.POST['search_field'])
                        context['search_error'] = False

                elif self.request.POST['category'] == 'Date':
                    all_externals = search_date('External', self.request.POST['search_field'])
                elif self.request.POST['category'] == 'Telephone':
                    all_externals = search_telephone('External', self.request.POST['search_field'])
                elif self.request.POST['category'] == 'Client Name':
                    all_externals = search_name('External', self.request.POST['search_field'])
                elif self.request.POST['category'] == 'All':
                    all_externals = search_all('External', self.request.POST['search_field'])

                if len(self.request.POST['search_field']) == 0:
                    context['badges'] = False
                else:
                    context['badges'] = True

            elif self.request.POST['action'] == 'Filter':

                if self.request.POST['fast_select'].isnumeric():
                    all_externals = Order.objects.filter(client='External').order_by('-created_date')[:int(self.request.POST['fast_select'])]
                    context['filter_badge'] = True
                else:
                    all_externals = Order.objects.filter(client='External').order_by('-created_date')
                    context['filter_badge'] = False


                context['search_form'] = forms.SearchForm
                context['filter_form'] = forms.FilterForm(self.request.POST)

        else:
            all_externals = Order.objects.filter(client='External').order_by('-created_date')[:80]
            context['search_form'] = forms.SearchForm
            context['filter_form'] = forms.FilterForm
            context['badges'] = False


        context['visible_items'] = len(all_externals)

        for external in all_externals:
            context['orders'].append(custom_classes.OrderObject(external))

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

def search_id(client, ID):
    return Order.objects.filter(client=client, ID=ID).order_by('-created_date')

def search_date(client, date):
    return Order.objects.filter(client=client, created_date__contains=date).order_by('-created_date')

def search_name(client, name):
    return Order.objects.filter(client=client, owner__icontains=name).order_by('-created_date')

def search_telephone(client, telephone):
    return Order.objects.filter(client=client, telephone__icontains=telephone).order_by('-created_date')

def search_all(client, search_kwd):
    return ( 
        # Order.objects.filter(client=client, ID=search_kwd).order_by('-created_date') |
        Order.objects.filter(client=client, created_date__contains=search_kwd).order_by('-created_date') |
        Order.objects.filter(client=client, owner__icontains=search_kwd).order_by('-created_date') |
        Order.objects.filter(client=client, telephone__icontains=search_kwd).order_by('-created_date')
    )


def react_response(request):

    return JsonResponse({
        # 'models':json.loads(serializers.serialize('json', Order.objects.all())),
        'models':json.loads(serializers.serialize('json', Order.objects.order_by('-created_date'))),
        })