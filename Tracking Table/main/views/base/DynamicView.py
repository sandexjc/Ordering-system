import base64
from datetime import datetime, time

from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

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
    allowed_sorts = ("asc", "desc")
    allowed_order_types = ("order", "offer")

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

    def get_sort(self):
        sort = (self.request.GET.get("sort") or "desc").lower()
        if sort in self.allowed_sorts:
            return sort
        return "desc"

    def get_order_types(self):
        if "order_type" in self.request.GET:
            return [
                value
                for value in self.request.GET.getlist("order_type")
                if value in self.allowed_order_types
            ]
        return [self.order_type]

    def get_date_bounds(self):
        start = parse_date(self.request.GET.get("start") or "")
        end = parse_date(self.request.GET.get("end") or "")
        start_dt = None
        end_dt = None
        if start is not None:
            start_dt = timezone.make_aware(datetime.combine(start, time.min))
        if end is not None:
            end_dt = timezone.make_aware(datetime.combine(end, time.max))
        return start_dt, end_dt

    def get_filtered_queryset(self):
        queryset = self.model.objects.for_list()
        queryset = queryset.of_types(*self.get_order_types())

        start_dt, end_dt = self.get_date_bounds()
        if start_dt is not None or end_dt is not None:
            queryset = queryset.created_between(start_dt, end_dt)

        if self.get_sort() == "asc":
            return queryset.first_created()
        return queryset.last_created()

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
            if timezone.is_naive(created_date):
                created_date = timezone.make_aware(created_date)
            return created_date, int(pk_str)
        except Exception:
            return None

    def apply_cursor(self, queryset, cursor, sort):
        if not cursor:
            return queryset

        decoded = self.decode_cursor(cursor)
        if decoded is None:
            return queryset

        created_date, pk = decoded
        if sort == "asc":
            return queryset.filter(
                Q(created_date__gt=created_date)
                | Q(created_date=created_date, pk__gt=pk)
            )
        return queryset.filter(
            Q(created_date__lt=created_date)
            | Q(created_date=created_date, pk__lt=pk)
        )

    def get_paginated_queryset(self, limit, cursor=None):
        sort = self.get_sort()
        queryset = self.apply_cursor(self.get_filtered_queryset(), cursor, sort)
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
