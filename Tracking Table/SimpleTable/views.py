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
        plate_forms = []
        edge_forms = []

        class ProgressForm:

            def __init__(self, order_id, form):
                self.order_id = order_id
                self.form = form

            def __str__(self):
                return self.form

        # class Object:

        #     def __init__(self, internal):
        #         self.order = internal
        #         self.material_eger = Plate.objects.filter(cutID=internal.pk, manufacturer='Egger')
        #         self.material_krono = Plate.objects.filter(cutID=internal.pk, manufacturer='Kronospan')
        #         self.material_edge = Edge.objects.filter(cutID=internal.pk)
        #         self.notes = Note.objects.filter(cutID=internal.pk)

        #     def __str__(self):
        #         return self.order

        if self.request.POST:
            # print(f'SEARCHED {kwargs["search_string"]}')
            context['search_form'] = forms.SearchForm(self.request.POST)
            context['search_string'] = kwargs["search_string"]

            results = []
            internals = []

            internals_ids = Order.objects.filter(
                client='Internal', 
                ID__contains=kwargs['search_string'])
            # print(internals_ids)
            results.append(internals_ids)

            internals_date = Order.objects.filter(
                client='Internal', 
                created_date__contains=kwargs['search_string'])
            # print(internals_date)
            results.append(internals_date)

            internals_name = Order.objects.filter(
                client='Internal', 
                owner__contains=kwargs['search_string'])
            # print(internals_name)
            results.append(internals_name)

            internals_telephone = Order.objects.filter(
                client='Internal', 
                telephone__contains=kwargs['search_string'])
            # print(internals_telephone)
            results.append(internals_telephone)

            for item in results:
                if len(item) != 0:
                    for res in item:
                        if res not in internals:
                            internals.append(res)
                            # print(f'APPENDED {res}')

            if len(kwargs['search_string']) == 0:
                context['badges'] = False
            else:
                context['badges'] = True

        else:
            internals = Order.objects.filter(client='Internal')
            context['search_form'] = forms.SearchForm
            context['badges'] = False

        for internal in internals:

            internal.material_eger = Plate.objects.filter(cutID=internal.pk, manufacturer='Egger')
            internal.material_krono = Plate.objects.filter(cutID=internal.pk, manufacturer='Kronospan')
            internal.material_edge = Edge.objects.filter(cutID=internal.pk)
            internal.notes = Note.objects.filter(cutID=internal.pk)

            plate_form = forms.PlateProgressFormSet(instance=internal)
            form_object = ProgressForm(internal.ID, plate_form)
            plate_forms.append(form_object)

            edge_form = forms.EdgeProgressFormSet(instance=internal)
            form_object = ProgressForm(internal.ID, edge_form)
            edge_forms.append(form_object)

        # print(type(internals)) --> QUERY SET !!!
        context['internals'] = internals
        context['update_forms'] = plate_forms
        context['edge_forms'] = edge_forms

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
        plate_forms = []
        edge_forms = []

        class ProgressForm:

            def __init__(self, order_id, form):
                self.order_id = order_id
                self.form = form

            def __str__(self):
                return self.form

        if self.request.POST:
            # print(f'SEARCHED {kwargs["search_string"]}')
            context['search_form'] = forms.SearchForm(self.request.POST)
            context['search_string'] = kwargs["search_string"]

            results = []
            externals = []

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
                        if res not in externals:
                            externals.append(res)
                            # print(f'APPENDED {res}')

            if len(kwargs['search_string']) == 0:
                context['badges'] = False
            else:
                context['badges'] = True
        else:
            externals = Order.objects.filter(client='External')
            context['search_form'] = forms.SearchForm
            context['badges'] = False

        for external in externals:

            external.material_eger = Plate.objects.filter(cutID=external.pk, manufacturer='Egger')
            external.material_krono = Plate.objects.filter(cutID=external.pk, manufacturer='Kronospan')
            external.material_edge = Edge.objects.filter(cutID=external.pk)
            external.notes = Note.objects.filter(cutID=external.pk)

            plate_form = forms.PlateProgressFormSet(instance=external)
            form_object = ProgressForm(external.ID, plate_form)
            plate_forms.append(form_object)

            edge_form = forms.EdgeProgressFormSet(instance=external)
            form_object = ProgressForm(external.ID, edge_form)
            edge_forms.append(form_object)

        # print(type(internals)) --> QUERY SET !!!
        context['externals'] = externals
        context['update_forms'] = plate_forms
        context['edge_forms'] = edge_forms


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