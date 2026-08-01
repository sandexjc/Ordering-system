from django.http import JsonResponse
from django.template.loader import render_to_string

from common.mixins import DynamicFeatureFlagRequiredMixin
from common.views import MainView


class DynamicView(DynamicFeatureFlagRequiredMixin, MainView):

    """
    Dynamic landing page container view.

    Hierarchy:
    LoginRequiredMixin
            \
             -> MainView -> DynamicView
            /
    TemplateView

    --- Fields inherited from MainView ---

    No explicit class fields inherited.

    """

    template_name = "dynamic/orders.html"
    default_navigation = "table"
    allowed_views = ("table", "vitrine")
    model = None
    order_type = "order"
    default_items_count = 100
    rows_template_name = None
    rows_context_name = "orders"

    def get_requested_view(self):
        requested_view = (
            self.request.POST.get("view")
            or self.request.GET.get("view")
            or self.default_navigation
        )
        if requested_view in self.allowed_views:
            return requested_view
        return self.default_navigation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_view = self.get_requested_view()
        context["nav_select"] = current_view
        context["orders"] = []
        context["visible_items"] = 0
        context["current_time"] = self.get_time_of_day()
        context["dynamic_mode"] = True
        context["current_dynamic_view"] = current_view
        return context

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_default_queryset(self):
        return self.model.objects.latest_by_count(self.order_type, self.default_items_count)

    def get_rows_context(self, rows):
        return {self.rows_context_name: rows}

    def render_rows_html(self, rows):
        return render_to_string(
            self.rows_template_name,
            self.get_rows_context(rows),
            request=self.request,
        )

    def render_rows_json_response(self):
        rows = list(self.get_default_queryset())
        rows_html = self.render_rows_html(rows)
        return JsonResponse(
            {
                "rows_html": rows_html,
                "visible_items": len(rows),
            }
        )

    def get(self, request, *args, **kwargs):
        if self.model is not None and self.rows_template_name:
            return self.render_rows_json_response()
        return super().get(request, *args, **kwargs)
