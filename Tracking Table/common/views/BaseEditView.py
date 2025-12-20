from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from common.service import CurrencyOperations

class BaseEditView(LoginRequiredMixin, UpdateView):

    """ A reusable base view for editing order model and related items objects. """

    # Subclasses must define the below properties
    note_form_class = None
    related_formsets = []
    fk_field_name = None
    redirect_url = None

    # --- Helpers --- #
    def get_formsets(self, data=None):
        # Create and return all related formsets
        return {
            name: formset_class(data, instance=self.object) if data else formset_class(instance=self.object)
            for name, formset_class in self.related_formsets.items()
        }
    

    # --- GET --- #
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formsets = kwargs.get("formsets") or self.get_formsets()
        context.update(formsets)

        if self.note_form_class:
            context["add_note"] = kwargs.get("add_note") or self.note_form_class()

        context["current_order"] = self.object
        context["currency"] = CurrencyOperations.get_currency(self.object.created_at.date())
        return context
    

    # --- POST --- #
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        order_form = self.get_form()
        formsets = self.get_formsets(data=self.request.POST)
        note_form = self.note_form_class(self.request.POST)

        all_valid = order_form.is_valid() and all(fs.is_valid() for fs in formsets.values())

        if all_valid:
            return self.form_valid(order_form, note_form, formsets)
        else:
            for formset in formsets.values():
                for error in formset.errors:
                    if error:
                        messages.error(request, error.as_text())
            return self.form_invalid(order_form, note_form, formsets)
        

    # --- Validation --- #
    def form_valid(self, order_form, note_form, formsets):
        user = self.request.user.first_name

        # handle order form
        self.object = order_form.save()

        # handle note form
        note = note_form.save(commit=False)
        note.user = user
        setattr(note, self.fk_field_name, self.object)
        if note.content:
            note.save()

        # Handle realated formsets
        for formset in formsets.values():
            instances = formset.save(commit=False)
            for item in instances:
                item.modified_by = user
                setattr(item, self.fk_field_name, self.object)
                item.save()
            
            for item in formset.deleted_objects:
                item.modified_by = user
                item.soft_delete()

        messages.success(self.request, "Промените са запазени успешно!")
        return redirect(self.redirect_url, self.object.pk)

    def form_invalid(self, order_form, note_form, formsets):
        messages.error(self.request, "Възникна грешка!")

        # Return formsets with current data and errors
        return self.render_to_response(self.get_context_data(
            form=order_form,
            add_note=note_form,
            formsets=formsets,
        ))
