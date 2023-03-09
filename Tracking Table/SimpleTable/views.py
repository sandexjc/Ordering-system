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
    template_name = 'internals.html'

    def get_context_data(self, **kwargs):
        context = super(Internals, self).get_context_data(**kwargs)
        context['internals'] = []
        context['filter_badge'] = True
        
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
                    if self.request.POST['search_field'].isnumeric():
                        all_internals = search_id('Internal', self.request.POST['search_field']).order_by('-ID')
                    else:
                        context['search_error'] = True

                elif self.request.POST['category'] == 'Date':
                    all_internals = search_date('Internal', self.request.POST['search_field']).order_by('-ID')

                elif self.request.POST['category'] == 'Telephone':
                    all_internals = search_telephone('Internal', self.request.POST['search_field']).order_by('-ID')

                elif self.request.POST['category'] == 'Client Name':
                    all_internals = search_name('Internal', self.request.POST['search_field']).order_by('-ID')

                else:
                    if len(self.request.POST['search_field']) != 0:
                        all_internals.extend(search_date('Internal', self.request.POST['search_field']))
                        all_internals.extend(search_telephone('Internal', self.request.POST['search_field']))
                        all_internals.extend(search_name('Internal', self.request.POST['search_field']))

                        if self.request.POST['search_field'].isnumeric():
                            all_internals.extend(search_id('Internal', self.request.POST['search_field']))

                all_internals = list(set(all_internals))

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
            all_internals = Order.objects.filter(client='Internal').order_by('-created_date')[:50]
            context['search_form'] = forms.SearchForm
            context['filter_form'] = forms.FilterForm
            context['badges'] = False

        context['visible_items'] = len(all_internals)

        for internal in all_internals:
            context['internals'].append(custom_classes.OrderObject(internal))

        current_time = time.localtime(time.time())

        if current_time.tm_hour in range(7, 9):
            context['current_time'] = 'Morning'
        elif current_time.tm_hour in range(10, 13):
            context['current_time'] = 'Day'
        elif current_time.tm_hour in range(14, 19):
            context['current_time'] = 'Afternoon'
        else:
            context['current_time'] = 'Night'

        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

class Externals(LoginRequiredMixin, TemplateView):
    template_name = 'externals.html'

    def get_context_data(self, **kwargs):
        context = super(Externals, self).get_context_data(**kwargs)
        context['externals'] = []
        context['filter_badge'] = True
        
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
                    if self.request.POST['search_field'].isnumeric():
                        all_externals = search_id('External', self.request.POST['search_field']).order_by('-ID')
                    else:
                        context['search_error'] = True

                elif self.request.POST['category'] == 'Date':
                    all_externals = search_date('External', self.request.POST['search_field']).order_by('-ID')

                elif self.request.POST['category'] == 'Telephone':
                    all_externals = search_telephone('External', self.request.POST['search_field']).order_by('-ID')

                elif self.request.POST['category'] == 'Client Name':
                    all_externals = search_name('External', self.request.POST['search_field']).order_by('-ID')

                else:
                    if len(self.request.POST['search_field']) != 0:
                        all_externals.extend(search_date('External', self.request.POST['search_field']))
                        all_externals.extend(search_telephone('External', self.request.POST['search_field']))
                        all_externals.extend(search_name('External', self.request.POST['search_field']))

                        if self.request.POST['search_field'].isnumeric():
                            all_externals.extend(search_id('External', self.request.POST['search_field']))

                all_externals = list(set(all_externals))

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
            all_externals = Order.objects.filter(client='External').order_by('-created_date')[:50]
            context['search_form'] = forms.SearchForm
            context['filter_form'] = forms.FilterForm
            context['badges'] = False


        context['visible_items'] = len(all_externals)

        for external in all_externals:
            context['externals'].append(custom_classes.OrderObject(external))

        current_time = time.localtime(time.time())

        if current_time.tm_hour in range(7, 9):
            context['current_time'] = 'Morning'
        elif current_time.tm_hour in range(10, 13):
            context['current_time'] = 'Day'
        elif current_time.tm_hour in range(14, 19):
            context['current_time'] = 'Afternoon'
        else:
            context['current_time'] = 'Night'

        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

def search_id(client, ID):

    return Order.objects.filter(
            client=client, 
            ID=ID,
            )

def search_date(client, date):

    return Order.objects.filter(
            client=client, 
            created_date__contains=date,
            )

def search_name(client, name):

    return Order.objects.filter(
            client=client, 
            owner__contains=name,
            )

def search_telephone(client, telephone):

    return Order.objects.filter(
            client=client, 
            telephone__contains=telephone,
            )

def react_response(request):

    return JsonResponse({
        # 'models':json.loads(serializers.serialize('json', Order.objects.all())),
        'models':json.loads(serializers.serialize('json', Order.objects.order_by('-created_date'))),
        })