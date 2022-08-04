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
            context['search_form'] = forms.SearchForm(self.request.POST)
            context['search_string'] = kwargs["search_string"]

            results = []
            all_internals = []

            internals_ids = Order.objects.filter(
                client='Internal', 
                ID__contains=kwargs['search_string'])
            results.append(internals_ids)

            internals_date = Order.objects.filter(
                client='Internal', 
                created_date__contains=kwargs['search_string'])
            results.append(internals_date)

            internals_name = Order.objects.filter(
                client='Internal', 
                owner__contains=kwargs['search_string'])
            results.append(internals_name)

            internals_telephone = Order.objects.filter(
                client='Internal', 
                telephone__contains=kwargs['search_string'])
            results.append(internals_telephone)

            for item in results:
                if len(item) != 0:
                    for res in item:
                        if res not in all_internals:
                            all_internals.append(res)

            if len(kwargs['search_string']) == 0:
                context['badges'] = False
            else:
                context['badges'] = True

        else:
            all_internals = Order.objects.filter(client='Internal')
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
        return self.render_to_response(self.get_context_data(search_string=self.request.POST['search_field']))

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
            context['search_string'] = kwargs["search_string"]

            results = []
            all_externals = []

            externals_ids = Order.objects.filter(
                client='External', 
                ID__contains=kwargs['search_string'])
            # print(externals_ids)
            results.append(externals_ids)

            externals_date = Order.objects.filter(
                client='External', 
                created_date__contains=kwargs['search_string'])
            # print(externals_date)
            results.append(externals_date)

            externals_name = Order.objects.filter(
                client='External', 
                owner__contains=kwargs['search_string'])
            # print(externals_name)
            results.append(externals_name)

            externals_telephone = Order.objects.filter(
                client='External', 
                telephone__contains=kwargs['search_string'])
            # print(externals_telephone)
            results.append(externals_telephone)

            for item in results:
                if len(item) != 0:
                    for res in item:
                        if res not in all_externals:
                            all_externals.append(res)

            if len(kwargs['search_string']) == 0:
                context['badges'] = False
            else:
                context['badges'] = True
        else:
            all_externals = Order.objects.filter(client='External')
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
        return self.render_to_response(self.get_context_data(search_string=self.request.POST['search_field']))