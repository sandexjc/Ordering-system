from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from table.models import Order, Plate, Edge, Payment, Note
from SimpleTable import forms
import time
import table

class Internals(LoginRequiredMixin, TemplateView):
    template_name = 'internals.html'

    def get_context_data(self, **kwargs):
        context = super(Internals, self).get_context_data(**kwargs)
        context['internals'] = []

        class OrderObject:

            def __init__(self, internal):
                self.order = internal
                self.material_eger = Plate.objects.filter(cutID=internal, manufacturer='Egger')
                self.material_krono = Plate.objects.filter(cutID=internal, manufacturer='Kronospan')
                self.material_edge = Edge.objects.filter(cutID=internal)
                self.notes = Note.objects.filter(cutID=internal)
                self.plate_forms = forms.PlateProgressFormSet(instance=internal)
                self.edge_forms = forms.EdgeProgressFormSet(instance=internal)

            def __str__(self):
                return str(self.order)

        if self.request.POST:

            print(kwargs['search_field'])
    
            context['search_form'] = forms.SearchForm(self.request.POST)
            context['category'] = kwargs['category']
            context['search_string'] = kwargs['search_field']

            results = []
            all_internals = []

            if kwargs['category'] == 'ID':
                all_internals.extend(search_id('Internal', kwargs['search_field']))

            elif kwargs['category'] == 'Date':
                all_internals.extend(search_date('Internal', kwargs['search_field']))

            elif kwargs['category'] == 'Telephone':
                all_internals.extend(search_telephone('Internal', kwargs['search_field']))

            elif kwargs['category'] == 'Client Name':
                all_internals.extend(search_name('Internal', kwargs['search_field']))

            else:
                all_internals.extend(search_id('Internal', kwargs['search_field']))
                all_internals.extend(search_date('Internal', kwargs['search_field']))
                all_internals.extend(search_telephone('Internal', kwargs['search_field']))
                all_internals.extend(search_name('Internal', kwargs['search_field']))

            all_internals = list(set(all_internals))

            if len(kwargs['search_field']) == 0:
                context['badges'] = False
            else:
                context['badges'] = True

        else:
            all_internals = Order.objects.filter(client='Internal').order_by('-ID')
            context['search_form'] = forms.SearchForm
            context['badges'] = False

        for internal in all_internals:
            context['internals'].append(OrderObject(internal))

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
        return self.render_to_response(self.get_context_data(
            search_field=self.request.POST['search_field'],
            category=self.request.POST['category']
            ))

class Externals(LoginRequiredMixin, TemplateView):
    template_name = 'externals.html'

    def get_context_data(self, **kwargs):
        context = super(Externals, self).get_context_data(**kwargs)
        context['externals'] = []

        class OrderObject:

            def __init__(self, external):
                self.order = external
                self.material_eger = Plate.objects.filter(cutID=external, manufacturer='Egger')
                self.material_krono = Plate.objects.filter(cutID=external, manufacturer='Kronospan')
                self.material_edge = Edge.objects.filter(cutID=external)
                self.notes = Note.objects.filter(cutID=external)
                self.plate_forms = forms.PlateProgressFormSet(instance=external)
                self.edge_forms = forms.EdgeProgressFormSet(instance=external)

            def __str__(self):
                return str(self.order)


        if self.request.POST:
            context['search_form'] = forms.SearchForm(self.request.POST)
            context['category'] = kwargs['category']
            context['search_string'] = kwargs['search_field']

            results = []
            all_externals = []

            if kwargs['category'] == 'ID':
                all_externals.extend(search_id('External', kwargs['search_field']))

            elif kwargs['category'] == 'Date':
                all_externals.extend(search_date('External', kwargs['search_field']))

            elif kwargs['category'] == 'Telephone':
                all_externals.extend(search_telephone('External', kwargs['search_field']))

            elif kwargs['category'] == 'Client Name':
                all_externals.extend(search_name('External', kwargs['search_field']))

            else:
                all_externals.extend(search_id('External', kwargs['search_field']))
                all_externals.extend(search_date('External', kwargs['search_field']))
                all_externals.extend(search_telephone('External', kwargs['search_field']))
                all_externals.extend(search_name('External', kwargs['search_field']))

            all_externals = list(set(all_externals))

            if len(kwargs['search_field']) == 0:
                context['badges'] = False
            else:
                context['badges'] = True
        else:
            all_externals = Order.objects.filter(client='External').order_by('-ID')
            context['search_form'] = forms.SearchForm
            context['badges'] = False

        for external in all_externals:
            context['externals'].append(OrderObject(external))

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
        return self.render_to_response(self.get_context_data(
            search_field=self.request.POST['search_field'],
            category=self.request.POST['category'],
            ))


def search_id(client, ID):

    return Order.objects.filter(
            client=client, 
            ID__contains=ID,
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