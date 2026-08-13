from common.views import BaseUpdateProgressStepView
from table.models import Edge, Order, Plate
from table.service.table.OrderReady import plates_make_order_ready

from django.core import serializers
from django.http import JsonResponse

import json


class UpdateProgressStep(BaseUpdateProgressStepView):

    """

    Hierarchy:
    DynamicFeatureFlagRequiredMixin -> BaseUpdateProgressStepView -> UpdateProgressStep
    LoginRequiredMixin -> BaseUpdateProgressStepView -> UpdateProgressStep
    View -> BaseUpdateProgressStepView -> UpdateProgressStep

    Dynamic table click-to-toggle for plate, edge, and order progress fields.

    --- Fields inherited from BaseUpdateProgressStepView ---

    model = None
    allowed_fields = {}
    http_method_names = ["post"]

    """

    model = Order
    allowed_fields = {
        "plate": ("ordered", "delivered", "cutted", "edged"),
        "edge": ("ordered", "delivered"),
        "order": ("order_taken", "invoice"),
    }

    def resolve_item(self, order, target, item_id):
        """Resolve the row to update; plate/edge ids must belong to this order."""
        if target == "order":
            return order, None

        if item_id in (None, ""):
            return None, JsonResponse({"error": "Missing item id"}, status=400)

        if target == "plate":
            item = Plate.objects.for_order(order).filter(pk=item_id).first()
        elif target == "edge":
            item = Edge.objects.for_order(order).filter(pk=item_id).first()
        else:
            item = None

        if item is None:
            return None, JsonResponse({"error": "Item not found"}, status=404)
        return item, None

    def is_step_disabled(self, order, target, item, field, value):
        """Same disabled rules as PlateProgressForm (client plates / offers)."""
        if target != "plate":
            return False
        if field == "ordered" and item.from_client:
            return True
        if field in ("cutted", "edged") and order.order_type == "offer":
            return True
        return False

    def apply_step_value(self, order, target, item, field, value):
        """Set the clicked step; plate/edge also fill or clear sequential neighbors."""
        if target not in ("plate", "edge"):
            return super().apply_step_value(order, target, item, field, value)

        fields = self.allowed_fields[target]
        field_index = fields.index(field)
        if value:
            fields_to_set = fields[: field_index + 1]
            new_value = True
        else:
            fields_to_set = fields[field_index:]
            new_value = False
        for step_field in fields_to_set:
            if not self.is_step_disabled(order, target, item, step_field, new_value):
                setattr(item, step_field, new_value)
        item.save()

    def after_step_applied(self, order, target, item, field, value):
        """Recompute order_ready; clear order_taken unless this POST was an order-level toggle."""
        order.order_ready = plates_make_order_ready(order)
        if not order.order_ready and target != "order":
            order.order_taken = False
        order.save()

    def serialize_response(self, order, target, item):
        """JSON in the same serializer shape as UpdateOrder, limited to the changed row."""
        payload = super().serialize_response(order, target, item)
        if target == "plate":
            payload["plates"] = json.loads(serializers.serialize("json", [item]))
        elif target == "edge":
            payload["edges"] = json.loads(serializers.serialize("json", [item]))
        return payload
