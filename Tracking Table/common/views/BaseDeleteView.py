from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import SingleObjectMixin
from django.views import View
from django.http import JsonResponse


class BaseDeleteView(LoginRequiredMixin, SingleObjectMixin, View):

    """ Reusable JSON-based common delete view for all apps.  """

    # Subclasses must define
    model = None

    def get_object(self, queryset=None):
        order = super().get_object(queryset)
        # FIXME - Add permissions checks later
        return order

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            self.object.soft_delete()
        except Exception as exc:
            return JsonResponse(
                {"status": "error", "message": str(exc)},
                status=500
            )

        return JsonResponse({"status": "ok", "id": self.object.pk})
