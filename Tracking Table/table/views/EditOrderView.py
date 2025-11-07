from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.contrib import messages

from table import models
from table import forms

from django.shortcuts import redirect

class EditOrder(LoginRequiredMixin, UpdateView):

    model = models.Order
    form_class = forms.EditOrderForm
    template_name = 'table/edit_order.html'
    
    def get_context_data(self, **kwargs):

        context = super(EditOrder, self).get_context_data(**kwargs)

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

        self.object = models.Order.objects.get_by_id(pk)
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

        plate = PLATES.save(commit=False)

        for item in plate:
            item.modified_by = user
            item.order_id = self.object
            item.save()

        for item in PLATES.deleted_objects:
            item.modified_by = user
            item.delete()

        cutting = CUTTING.save(commit=False)

        for item in cutting:
            item.modified_by = user
            item.order_id = self.object
            item.save()

        for item in CUTTING.deleted_objects:
            item.modified_by = user
            item.delete()

        edge = EDGES.save(commit=False)

        for item in edge:
            item.modified_by = user
            item.order_id = self.object
            item.save()

        for item in EDGES.deleted_objects:
            item.modified_by = user
            item.delete()

        edging = EDGING.save(commit=False)

        for item in edging:
            item.modified_by = user
            item.order_id = self.object
            item.save()

        for item in EDGING.deleted_objects:
            item.modified_by = user
            item.delete()

        other = OTHER.save(commit=False)

        for item in other:
            item.modified_by = user
            item.order_id = self.object
            item.save()

        for item in OTHER.deleted_objects:
            item.modified_by = user
            item.delete()

        payment = PAYMENTS.save(commit=False)

        for item in payment:
            item.modified_by = user
            item.order_id = self.object
            item.save()

        self.object.save()

        return redirect('table:editOrder', self.object.pk)

    def form_invalid(self, form, PLATES, EDGES, PAYMENTS, CUTTING, EDGING, OTHER, user, add_note):
        return self.render_to_response(self.get_context_data(form=form, 
            PLATES=PLATES, EDGES=EDGES, PAYMENTS=PAYMENTS, 
            CUTTING=CUTTING, EDGING=EDGING, OTHER=OTHER, add_note=add_note))