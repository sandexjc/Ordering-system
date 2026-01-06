from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.shortcuts import redirect
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.core import serializers
from django.db import transaction
import json


class BaseUpdateView(LoginRequiredMixin, UpdateView):
    
    """ Shared update progress logic for all apps. """

    # must be defined in subclasses
    model = None
    form_class = None
    success_url = "/"

    # --- Hooks --- #

    def get_extra_forms(self):
        # Return a dict of extra forms/formsets.
        return {}

    def handle_extra_forms(self, forms):
        # Save or process extra forms.
        pass

    def is_order_ready(self, order_instance, forms):
        # Determine if order is ready.
        return order_instance.order_ready

    # --- Core logic --- #

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(request, "Тази поръчка не може да бъде достъпена!")
            return redirect(self.success_url)

        order_form = self.get_form()
        extra_forms = self.get_extra_forms()

        all_valid = order_form.is_valid() and all(
            form.is_valid() for form in extra_forms.values()
        )

        if not all_valid:
            self.add_form_errors(order_form, extra_forms)
            return redirect(self.success_url)

        return self.form_valid(order_form, extra_forms)

    @transaction.atomic
    def form_valid(self, order_form, extra_forms):

        order_instance = order_form.save(commit=False)
        self.handle_extra_forms(extra_forms)

        order_instance.order_ready = self.is_order_ready(order_instance, extra_forms)
        if not order_instance.order_ready:
            order_instance.order_taken = False

        order_instance.save()

        return JsonResponse(self.serialize_response(order_instance))

    # --- Utilities --- #

    def add_form_errors(self, order_form, extra_forms):
        for field, errors in order_form.errors.items():
            for error in errors:
                messages.error(self.request, error)

        for form in extra_forms.values():
            for error_list in form.errors:
                for error in error_list.values():
                    messages.error(self.request, error)

    def serialize_response(self, order_instance):
        return {
            "order": json.loads(serializers.serialize("json", [order_instance])),
        }
