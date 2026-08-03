import base64

from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.dateparse import parse_datetime

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
    page_size = 50
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

    def get_page_size(self):
        raw_limit = self.request.GET.get("limit")
        if raw_limit and raw_limit.isnumeric():
            return max(1, min(int(raw_limit), 100))
        return self.page_size

    def encode_cursor(self, order):
        raw = f"{order.created_date.isoformat()}|{order.pk}"
        return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")

    def decode_cursor(self, cursor):
        try:
            raw = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
            date_str, pk_str = raw.rsplit("|", 1)
            created_date = parse_datetime(date_str)
            if created_date is None:
                return None
            return created_date, int(pk_str)
        except Exception:
            return None

    def get_paginated_queryset(self, limit, cursor=None):
        queryset = self.model.objects.all_by_order_type(self.order_type)

        if cursor:
            decoded = self.decode_cursor(cursor)
            if decoded is not None:
                created_date, pk = decoded
                queryset = queryset.filter(
                    Q(created_date__lt=created_date)
                    | Q(created_date=created_date, pk__lt=pk)
                )

        # Fetch one extra row to detect whether more pages exist.
        return list(queryset[: limit + 1])

    def get_rows_context(self, rows):
        return {self.rows_context_name: rows}

    def render_rows_html(self, rows):
        return render_to_string(
            self.rows_template_name,
            self.get_rows_context(rows),
            request=self.request,
        )

    def render_rows_json_response(self):
        limit = self.get_page_size()
        cursor = self.request.GET.get("cursor") or None
        rows = self.get_paginated_queryset(limit, cursor)
        has_more = len(rows) > limit
        page_rows = rows[:limit]
        next_cursor = self.encode_cursor(page_rows[-1]) if has_more and page_rows else None
        rows_html = self.render_rows_html(page_rows) if page_rows else ""

        return JsonResponse(
            {
                "rows_html": rows_html,
                "visible_items": len(page_rows),
                "has_more": has_more,
                "next_cursor": next_cursor,
            }
        )

    def get(self, request, *args, **kwargs):
        if self.model is not None and self.rows_template_name:
            return self.render_rows_json_response()
        return super().get(request, *args, **kwargs)
