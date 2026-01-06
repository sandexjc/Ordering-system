from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.core import serializers

from common.views import BaseUpdateView
from table.models import Order
from table.forms import PlateProgressFormSet, EdgeProgressFormSet, OrderProgressForm

import json

class UpdateOrder(BaseUpdateView):

    """ Update table app orders progress class. """

    model = Order
    form_class = OrderProgressForm

    def get_extra_forms(self):
        return {
            "plates": PlateProgressFormSet(self.request.POST, instance=self.object),
            "edges": EdgeProgressFormSet(self.request.POST, instance=self.object),
        }

    def handle_extra_forms(self, forms):
        plates = forms["plates"].save(commit=False)
        edges = forms["edges"].save(commit=False)

        for item in plates:
            item.save()

        for item in edges:
            item.save()

    def is_order_ready(self, order_instance, forms):
        plates = forms["plates"].save(commit=False)
        for item in plates:
            if not item.delivered or not item.cutted or not item.edged:
                return False
        return True

    def serialize_response(self, order_instance):
        return {
            "order": json.loads(serializers.serialize("json", [order_instance])),
            "plates": json.loads(
                serializers.serialize(
                    "json", order_instance.plates.model.objects.for_order(order_instance)
                    )
                ),
            "edges": json.loads(
                serializers.serialize(
                    "json", order_instance.edges.model.objects.for_order(order_instance)
                    )
                ),
        }