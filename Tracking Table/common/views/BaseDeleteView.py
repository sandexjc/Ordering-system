from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic.detail import SingleObjectMixin


@method_decorator(csrf_protect, name="dispatch")
class BaseDeleteView(LoginRequiredMixin, SingleObjectMixin, View):

    """

    Hierarchy:
    LoginRequiredMixin -> BaseDeleteView
    SingleObjectMixin -> BaseDeleteView
    View -> BaseDeleteView

    Shared JSON POST for order / vitrine delete (static modal + dynamic row).

    Security:
    - login required
    - CSRF required (middleware + csrf_protect; client sends X-CSRFToken)
    - POST only

    --- Fields inherited from LoginRequiredMixin ---

    No explicit class fields inherited.

    --- Fields inherited from SingleObjectMixin ---

    No explicit class fields inherited.

    --- Fields inherited from View ---

    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]

    """

    # Subclasses must define
    model = None
    http_method_names = ["post"]

    def get_object(self, queryset=None):
        order = super().get_object(queryset)
        # FIXME - Add permissions checks later
        return order

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        
        try:
            self.object = self.get_object()
        except (Http404, ObjectDoesNotExist):
            # Already deleted (soft-deleted rows 404 from the default manager)
            return JsonResponse({"status": "ok"})

        try:
            # Run custom workflow delete sequence
            self.object.run_workflow_delete()
        except Exception as exc:
            return JsonResponse(
                {"status": "error", "message": str(exc)},
                status=500
            )

        return JsonResponse({"status": "ok", "id": self.object.pk})
