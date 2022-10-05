from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView, TemplateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.core import serializers

from lib import custom_classes
from accounts.models import User
from table.models import Order, Plate, Edge, Payment, Cutting, Edging, Other, Change 
from table import forms
from SimpleTable.forms import PlateProgressFormSet, EdgeProgressFormSet, UpdateOrderProgressForm
import json

class CreateOrder(LoginRequiredMixin, CreateView):

    form_class = forms.CreateOrderForm
    template_name = 'table/newOrder.html'

    def get_context_data(self, **kwargs):
        context = super(CreateOrder, self).get_context_data(**kwargs)
        context['add_note'] = forms.AddNoteForm

        return context

    def post(self, request):

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        note = self.request.POST['content']
        user = self.request.user

        return self.form_valid(form, note, user)

    def form_valid(self, form, note, user):

        self.object = form.save(commit=False)
        self.object.save()

        Change.objects.create(
            cutID=self.object,
            user=user.first_name, 
            operation='created', 
            what='Order',
            new_state=self.object.ID,
            ).save()

        add_note = forms.AddNoteForm(self.request.POST).save(commit=False)
        add_note.cutID = self.object
        add_note.user = user
        add_note.content = note

        if note != '':
            add_note.save()

            Change.objects.create(
            cutID=self.object,
            user=user.first_name, 
            operation='created', 
            what='Note',
            new_state=note,
            ).save()

        return redirect('table:editOrder', self.object.pk)

class EditOrder(LoginRequiredMixin, UpdateView):

    model = Order
    form_class = forms.UpdateOrderForm
    template_name = 'table/editOrder.html'
    
    def get_context_data(self, **kwargs):

        context = super(EditOrder, self).get_context_data(**kwargs)

        self.object.update()

        if self.request.POST:
            context['plate_forms'] = kwargs['PLATES']
            context['cutting_forms'] = kwargs['CUTTING']
            context['edge_forms'] = kwargs['EDGES']
            context['edging_forms'] = kwargs['EDGING']
            context['others_forms'] = kwargs['OTHER']
            context['payment_forms'] = kwargs['PAYMENTS']
            context['add_note'] = kwargs['add_note']
        else:
            context['plate_forms'] = forms.PlateFormSet(instance=self.object)
            context['cutting_forms'] = forms.CuttingFormSet(instance=self.object)
            context['edge_forms'] = forms.EdgeFormSet(instance=self.object)
            context['edging_forms'] = forms.EdgingFormSet(instance=self.object)
            context['others_forms'] = forms.OthersFormSet(instance=self.object)
            context['payment_forms'] = forms.PaymentFormSet(instance=self.object)
            context['add_note'] = forms.AddNoteForm

        context['current_plates'] = Plate.objects.filter(cutID=self.object)
        context['current_edges'] = Edge.objects.filter(cutID=self.object)
        context['current_payments'] = Payment.objects.filter(cutID=self.object)
        context['current_order'] = self.object

        return context

    def post(self, request, pk, *args, **kwargs):

        self.object = Order.objects.get(pk=pk)
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        add_note = forms.AddNoteForm(self.request.POST)
        note = self.request.POST['content']
        user = self.request.user.first_name

        all_tables = []

        PLATES = forms.PlateFormSet(self.request.POST, instance=self.object)
        all_tables.append(PLATES)
        CUTTING = forms.CuttingFormSet(self.request.POST, instance=self.object)
        all_tables.append(CUTTING)
        EDGES = forms.EdgeFormSet(self.request.POST, instance=self.object)
        all_tables.append(EDGES)
        EDGING = forms.EdgingFormSet(self.request.POST, instance=self.object)
        all_tables.append(EDGING)
        OTHER = forms.OthersFormSet(self.request.POST, instance=self.object)
        all_tables.append(OTHER)
        PAYMENTS = forms.PaymentFormSet(self.request.POST, instance=self.object)
        all_tables.append(PAYMENTS)

        if form.is_valid() and PLATES.is_valid() and EDGES.is_valid() and PAYMENTS.is_valid() and CUTTING.is_valid() and EDGING.is_valid() and OTHER.is_valid():
            messages.success(request, 'SAVED SUCCESSFULLY')
            return self.form_valid(form, PLATES, EDGES, PAYMENTS, CUTTING, EDGING, OTHER, add_note, user, note)
        else:
            messages.error(request, 'INVALID FORM')

            for table in all_tables:

                for error in table.errors:
                    if error:
                        messages.error(request, error.as_text())

                for row in table:
                    for field in row.fields:
                        if row.has_error(field, code=None):

                            if field in ['price']:
                                row.fields[field].widget.attrs = {
                                'class': 'form-control form-control-sm is-invalid', 
                                'step': '0.01',
                                'style': 'width: 90px',
                                }

                            elif field in ['quantity']:
                                row.fields[field].widget.attrs = {
                                'class': 'form-control form-control-sm is-invalid',
                                'style': 'width: 75px',
                                }

                            elif field in ['cutting_type', 'edging_type', 'description']:
                                row.fields[field].widget.attrs = {
                                'class': 'form-control form-control-sm is-invalid',
                                'style': 'width: 200px',
                                }

                            elif field in ['material']:
                                row.fields[field].widget.attrs = {
                                'class': 'form-control form-control-sm is-invalid',
                                'style': 'width: 170px',
                                }

                            else:
                                row.fields[field].widget.attrs = {
                                'class': 'form-control form-control-sm is-invalid',
                                'style': 'width: 100px',
                                }

            return self.form_invalid(form, PLATES, EDGES, PAYMENTS, CUTTING, EDGING, OTHER, user, add_note)

    def form_valid(self, form, PLATES, EDGES, PAYMENTS, CUTTING, EDGING, OTHER, add_note, user, note):

        self.object = form.save(commit=False)
        self.object.save()

        notes = add_note.save(commit=False)
        notes.user = user
        notes.cutID = self.object
        notes.content = note

        if note != '':
            notes.save()

            Change.objects.create(
            cutID=self.object,
            user=user, 
            operation='created', 
            what='Note',
            new_state=note,
            ).save()

        plate = PLATES.save(commit=False)

        for item in plate:

            if item.pk:

                old_object = Plate.objects.get(pk=item.pk)
                changed_fields = {}

                if old_object.material != item.material:
                    changed_fields['material'] = f'{old_object.material} -> {item.material}'

                if old_object.manufacturer != item.manufacturer:
                    changed_fields['manufacturer'] = f'{old_object.manufacturer} -> {item.manufacturer}'

                if old_object.quantity != item.quantity:
                    changed_fields['quantity'] = f'{old_object.quantity} -> {item.quantity}'

                if old_object.price != item.price:
                    changed_fields['price'] = f'{old_object.price} -> {item.price}'

                if old_object.from_client != item.from_client:
                    changed_fields['from_client'] = f'{old_object.from_client} -> {item.from_client}'



                print(changed_fields)

                for changed_field in changed_fields.keys():
                    Change.objects.create(
                    cutID=self.object,
                    user=user, 
                    operation='Changed', 
                    what=changed_field,
                    current_state=item.material,
                    new_state=changed_fields[changed_field],
                    ).save()
            else:
                Change.objects.create(
                cutID=self.object,
                user=user, 
                operation='Added', 
                what='Plate',
                new_state=item.material,
                ).save()

            item.cutID = self.object
            item.value = round((item.quantity * item.price), 2)
            item.save()

        for item in PLATES.deleted_objects:
            item.delete()

            Change.objects.create(
            cutID=self.object,
            user=user, 
            operation='Deleted', 
            what='Plate',
            new_state=item.material,
            ).save()

        cutting = CUTTING.save(commit=False)

        for item in cutting:

            if item.pk:

                old_object = Cutting.objects.get(pk=item.pk)
                changed_fields = {}

                if old_object.cutting_type != item.cutting_type:
                    changed_fields['cutting_type'] = f'{old_object.cutting_type} -> {item.cutting_type}'

                if old_object.quantity != item.quantity:
                    changed_fields['quantity'] = f'{old_object.quantity} -> {item.quantity}'

                if old_object.price != item.price:
                    changed_fields['price'] = f'{old_object.price} -> {item.price}'

                print(changed_fields)

                for changed_field in changed_fields.keys():
                    Change.objects.create(
                    cutID=self.object,
                    user=user, 
                    operation='Changed', 
                    what=changed_field,
                    current_state=item.cutting_type,
                    new_state=changed_fields[changed_field],
                    ).save()
            else:
                Change.objects.create(
                cutID=self.object,
                user=user, 
                operation='Added', 
                what='Cutting',
                new_state=item.cutting_type,
                ).save()

            item.cutID = self.object
            item.value = round((item.quantity * item.price), 2)
            item.save()

        for item in CUTTING.deleted_objects:

            Change.objects.create(
            cutID=self.object,
            user=user, 
            operation='Deleted', 
            what='Cutting',
            new_state=item.cutting_type,
            ).save()

            item.delete()

        edge = EDGES.save(commit=False)

        for item in edge:
            item.cutID = self.object
            item.value = round((item.quantity * item.price), 2)
            item.save()

        for item in EDGES.deleted_objects:
            print(f'DELETING {item}')
            item.delete()

        edging = EDGING.save(commit=False)

        for item in edging:
            item.cutID = self.object
            item.value = round((item.quantity * item.price), 2)
            item.save()

        for item in EDGING.deleted_objects:
            print(f'DELETING {item}')
            item.delete()

        other = OTHER.save(commit=False)

        for item in other:
            item.cutID = self.object
            item.value = round((item.quantity * item.price), 2)
            item.save()

        for item in OTHER.deleted_objects:
            print(f'DELETING {item}')
            item.delete()

        payment = PAYMENTS.save(commit=False)

        for item in payment:
            item.cutID = self.object
            item.save()


        self.object.update()
        self.object.save()

        return redirect('table:editOrder', self.object.pk)

    def form_invalid(self, form, PLATES, EDGES, PAYMENTS, CUTTING, EDGING, OTHER, user, add_note):
        return self.render_to_response(self.get_context_data(form=form, 
            PLATES=PLATES, EDGES=EDGES, PAYMENTS=PAYMENTS, 
            CUTTING=CUTTING, EDGING=EDGING, OTHER=OTHER, add_note=add_note))

class DeleteOrder(LoginRequiredMixin, DeleteView):

    model = Order
    
    def post(self, request, pk, *args, **kwargs):

        self.object = Order.objects.get(pk=pk)
        print('DELETING OBJECT ->',self.object)

        self.object.delete()

        return JsonResponse({
            'status':'OK',
            })


class UpdateOrder(LoginRequiredMixin, UpdateView):

    model = Order

    def post(self, request, pk, *args, **kwargs):

        print('UPDATE ORDER ->', pk)

        self.object = Order.objects.get(pk=pk)
        PLATES_PROG = PlateProgressFormSet(self.request.POST, instance=self.object)
        EDGES_PROG = EdgeProgressFormSet(self.request.POST, instance=self.object)
        ORDER_PROG = UpdateOrderProgressForm(self.request.POST, instance=self.object)

        print('<<--------------------------------->>')

        if PLATES_PROG.is_valid() and EDGES_PROG.is_valid() and ORDER_PROG.is_valid():
            print('FORM VALID')
            return self.form_valid(PLATES_PROG, EDGES_PROG, ORDER_PROG, self.object)
        else:
            print('FORM INVALID _____________')
            print('PLATES ERRORS:')
            print(PLATES_PROG.errors)
            print('EDGES ERRORS:')
            print(EDGES_PROG.errors)
            return redirect('/')

    def form_valid(self, PLATES_PROG, EDGES_PROG, ORDER_PROG, order):

        plates_data = PLATES_PROG.save(commit=False)
        edges_data = EDGES_PROG.save(commit=False)

        for item in plates_data:
            item.save()

        for item in edges_data:
            item.save()

        if self.check_if_ready(order, plates_data, edges_data):
            order.order_ready = True
            order.save()
            ORDER_PROG.save()
        else:
            order.order_ready = False
            order.order_taken = False
            order.save()

        customObj = custom_classes.OrderDetails(order)
        
        return JsonResponse({
            'order': customObj.get_order(),
            'plates':customObj.get_plates(),
            'edges':customObj.get_edges(),
            })

    def check_if_ready(self, order, plates, edges):

        for item in plates:
            if not item.ordered or not item.delivered or not item.cutted or not item.edged:
                return False

        return True

class GetOrderHistory(LoginRequiredMixin, ListView):

    model = Order

    def get(self, request, pk, *args, **kwargs):

        print("GET ORDER HISTORY", pk)

        order_chnages = Change.objects.filter(cutID=pk)

        if not order_chnages:
            return JsonResponse({
            'changes': 'NO DATA',
            }) 
            
        return JsonResponse({
            'changes': json.loads(serializers.serialize('json', Change.objects.filter(cutID=pk))),
            })



class PrintOrder(LoginRequiredMixin, TemplateView):

    model = Order
    template_name = 'table/printOrder.html'
    
    def get_context_data(self, pk, **kwargs):

        context = super(PrintOrder, self).get_context_data(**kwargs)

        context['order'] = Order.objects.get(pk=pk)
        context['order_plates'] = Plate.objects.filter(cutID=pk)
        context['order_edges'] = Edge.objects.filter(cutID=pk)
        context['order_cutting'] = Cutting.objects.filter(cutID=pk)
        context['order_edging'] = Edging.objects.filter(cutID=pk)
        context['order_others'] = Other.objects.filter(cutID=pk)
        context['order_payments'] = Payment.objects.filter(cutID=pk)

        return context