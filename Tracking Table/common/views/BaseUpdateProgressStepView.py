from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.db import transaction
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from common.mixins import DynamicFeatureFlagRequiredMixin

import json


@method_decorator(csrf_protect, name="dispatch")
class BaseUpdateProgressStepView(DynamicFeatureFlagRequiredMixin, LoginRequiredMixin, View):

    """

    Hierarchy:
    DynamicFeatureFlagRequiredMixin -> BaseUpdateProgressStepView
    LoginRequiredMixin -> BaseUpdateProgressStepView
    View -> BaseUpdateProgressStepView

    Shared JSON POST for dynamic click-to-toggle progress steps.

    Security:
    - login required
    - CSRF required (middleware + csrf_protect; client sends X-CSRFToken)
    - POST only
    - field allowlist (`allowed_fields`)
    - 404 when DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING is off

    --- Fields inherited from DynamicFeatureFlagRequiredMixin ---

    feature_setting_name = "DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING"

    --- Fields inherited from LoginRequiredMixin ---

    No explicit class fields inherited.

    --- Fields inherited from View ---

    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]

    """

    model = None
    allowed_fields = {}
    http_method_names = ["post"]

    # --- Hooks --- #

    def resolve_item(self, order, target, item_id):
        # Return the row to update. Default: order-level fields only.
        if target == "order":
            return order, None
        return None, JsonResponse({"error": "Item not found"}, status=404)

    def is_step_disabled(self, order, target, item, field, value):
        # Block a click that must not change this step.
        return False

    def apply_step_value(self, order, target, item, field, value):
        # Set the clicked field. Subclasses may fill sequential neighbors.
        setattr(item, field, value)
        item.save()

    def after_step_applied(self, order, target, item, field, value):
        # Recompute derived flags (order_ready / order_taken) after the save.
        pass

    def serialize_response(self, order, target, item):
        # Same `{ order: [...] }` shape as BaseUpdateView.
        return {
            "order": json.loads(serializers.serialize("json", [order])),
        }

    # --- Core logic --- #

    def post(self, request, pk):
        order = self.model.objects.get_by_id(pk)
        if order is None:
            return JsonResponse({"error": "Order not found"}, status=404)

        payload, error_response = self.parse_payload(request)
        if error_response is not None:
            return error_response

        target = payload["target"]
        field = payload["field"]
        value = payload["value"]
        item_id = payload["item_id"]

        allowed = self.allowed_fields.get(target)
        if allowed is None or field not in allowed:
            return JsonResponse({"error": "Invalid progress field"}, status=400)

        item, error_response = self.resolve_item(order, target, item_id)
        if error_response is not None:
            return error_response

        if self.is_step_disabled(order, target, item, field, value):
            return JsonResponse({"error": "Progress step is disabled"}, status=400)

        with transaction.atomic():
            self.apply_step_value(order, target, item, field, value)
            self.after_step_applied(order, target, item, field, value)

        return JsonResponse(self.serialize_response(order, target, item))

    # --- Utilities --- #

    def parse_payload(self, request):
        """Read JSON or form POST into {target, field, value, item_id}."""
        try:
            if request.content_type and "application/json" in request.content_type:
                data = json.loads(request.body.decode("utf-8") or "{}")
            else:
                data = request.POST
        except (TypeError, ValueError, json.JSONDecodeError):
            return None, JsonResponse({"error": "Invalid request body"}, status=400)

        target = (data.get("target") or "").strip()
        field = (data.get("field") or "").strip()
        raw_item_id = data.get("item_id")
        try:
            value = self.parse_bool(data.get("value"))
        except (TypeError, ValueError):
            return None, JsonResponse({"error": "Invalid value"}, status=400)

        item_id = raw_item_id
        if item_id not in (None, ""):
            try:
                item_id = int(item_id)
            except (TypeError, ValueError):
                return None, JsonResponse({"error": "Invalid item id"}, status=400)

        return (
            {
                "target": target,
                "field": field,
                "value": value,
                "item_id": item_id,
            },
            None,
        )

    def parse_bool(self, value):
        """Accept JSON booleans or common form-encoded true/false strings."""
        if isinstance(value, bool):
            return value
        if value in (0, 1):
            return bool(value)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in ("true", "1", "yes"):
                return True
            if lowered in ("false", "0", "no"):
                return False
        raise ValueError("Expected a boolean")
