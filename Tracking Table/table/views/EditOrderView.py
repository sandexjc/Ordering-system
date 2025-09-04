from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.contrib import messages

from table import models
from table import forms

from django.shortcuts import redirect

class EditOrder(LoginRequiredMixin, UpdateView):

    model = models.Order
    form_class = forms.EditOrderForm
    template_name = 'table/editOrder.html'
    
    def get_context_data(self, **kwargs):

        context = super(EditOrder, self).get_context_data(**kwargs)

        # FIXME
        # Temporary move order object and total price calculation upon
        # creation of common managers and querysets for models.
        
        # self.object.update()

        self.object.clear()

        for item in models.Plate.objects.filter(order_id=self.object.id):
            self.object.plates_total += item.value
            self.object.total_price += item.value

        for item in models.Edge.objects.filter(order_id=self.object.id):
            self.object.edge_total += item.value
            self.object.total_price += item.value

        for item in models.Cutting.objects.filter(order_id=self.object.id):
            self.object.cutting_total += item.value
            self.object.total_price += item.value

        for item in models.Edging.objects.filter(order_id=self.object.id):
            self.object.edging_total += item.value
            self.object.total_price += item.value

        for item in models.Other.objects.filter(order_id=self.object.id):
            self.object.others_total += item.value
            self.object.total_price += item.value

        for item in models.Payment.objects.filter(order_id=self.object.id):
            self.object.paid += item.value

        self.object.balance = round((self.object.paid - self.object.total_price), 2)

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

        context['current_plates'] = models.Plate.objects.filter(order_id=self.object)
        context['current_edges'] = models.Edge.objects.filter(order_id=self.object)
        context['current_payments'] = models.Payment.objects.filter(order_id=self.object)
        context['current_order'] = self.object

        return context

    def post(self, request, pk, *args, **kwargs):

        self.object = models.Order.objects.get(pk=pk)
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
        notes.order_id = self.object
        notes.content = note

        if note != '':
            notes.save()

            models.Change.objects.create(order_id=self.object, user=user, operation='created', 
                                            what='Note', new_state=note).save()

        plate = PLATES.save(commit=False)

        for item in plate:

            if item.pk:

                old_object = models.Plate.objects.get(pk=item.pk)
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

                for changed_field in changed_fields.keys():
                    models.Change.objects.create(order_id=self.object, user=user, operation='Changed', what=changed_field,
                                                    current_state=item.material, new_state=changed_fields[changed_field]).save()
            else:
                models.Change.objects.create(order_id=self.object, user=user, operation='Added', 
                                                what='Plate', new_state=item.material).save()

            item.order_id = self.object
            item.value = round((item.quantity * item.price), 2)
            item.save()

        for item in PLATES.deleted_objects:
            item.delete()

            models.Change.objects.create(order_id=self.object, user=user, operation='Deleted', 
                                            what='Plate', new_state=item.material).save()

        cutting = CUTTING.save(commit=False)

        for item in cutting:

            if item.pk:

                old_object = models.Cutting.objects.get(pk=item.pk)
                changed_fields = {}

                if old_object.cutting_type != item.cutting_type:
                    changed_fields['cutting_type'] = f'{old_object.cutting_type} -> {item.cutting_type}'

                if old_object.quantity != item.quantity:
                    changed_fields['quantity'] = f'{old_object.quantity} -> {item.quantity}'

                if old_object.price != item.price:
                    changed_fields['price'] = f'{old_object.price} -> {item.price}'

                for changed_field in changed_fields.keys():
                    models.Change.objects.create(order_id=self.object, user=user, operation='Changed', what=changed_field,
                                                    current_state=item.cutting_type, new_state=changed_fields[changed_field]).save()
            else:
                models.Change.objects.create(order_id=self.object, user=user, operation='Added', 
                                                what='Cutting', new_state=item.cutting_type).save()

            item.order_id = self.object
            item.value = round((item.quantity * item.price), 2)
            item.save()

        for item in CUTTING.deleted_objects:

            models.Change.objects.create(order_id=self.object, user=user, operation='Deleted', 
                                            what='Cutting', new_state=item.cutting_type).save()

            item.delete()

        edge = EDGES.save(commit=False)

        for item in edge:
            item.order_id = self.object
            item.value = round((item.quantity * item.price), 2)
            item.save()

        for item in EDGES.deleted_objects:
            print(f'DELETING {item}')
            item.delete()

        edging = EDGING.save(commit=False)

        for item in edging:
            item.order_id = self.object
            item.value = round((item.quantity * item.price), 2)
            item.save()

        for item in EDGING.deleted_objects:
            print(f'DELETING {item}')
            item.delete()

        other = OTHER.save(commit=False)

        for item in other:
            item.order_id = self.object
            item.value = round((item.quantity * item.price), 2)
            item.save()

        for item in OTHER.deleted_objects:
            print(f'DELETING {item}')
            item.delete()

        payment = PAYMENTS.save(commit=False)

        for item in payment:
            item.order_id = self.object
            item.save()



        # FIXME
        # Temporary move order object and total price calculation upon
        # creation of common managers and querysets for models.

        # self.object.update()

        self.object.clear()

        for item in models.Plate.objects.filter(order_id=self.object.id):
            self.object.plates_total += item.value
            self.object.total_price += item.value

        for item in models.Edge.objects.filter(order_id=self.object.id):
            self.object.edge_total += item.value
            self.object.total_price += item.value

        for item in models.Cutting.objects.filter(order_id=self.object.id):
            self.object.cutting_total += item.value
            self.object.total_price += item.value

        for item in models.Edging.objects.filter(order_id=self.object.id):
            self.object.edging_total += item.value
            self.object.total_price += item.value

        for item in models.Other.objects.filter(order_id=self.object.id):
            self.object.others_total += item.value
            self.object.total_price += item.value

        for item in models.Payment.objects.filter(order_id=self.object.id):
            self.object.paid += item.value

        self.object.balance = round((self.object.paid - self.object.total_price), 2)

        self.object.save()

        return redirect('table:editOrder', self.object.pk)

    def form_invalid(self, form, PLATES, EDGES, PAYMENTS, CUTTING, EDGING, OTHER, user, add_note):
        return self.render_to_response(self.get_context_data(form=form, 
            PLATES=PLATES, EDGES=EDGES, PAYMENTS=PAYMENTS, 
            CUTTING=CUTTING, EDGING=EDGING, OTHER=OTHER, add_note=add_note))