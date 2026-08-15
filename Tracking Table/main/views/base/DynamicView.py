import base64
from datetime import datetime, time, timezone as datetime_timezone
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db.models import Max, Min, Q
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
    allowed_sort_by = ("order_id", "date", "balance")
    allowed_order_types = ("order", "offer")
    sync_delta_limit = 50
    sort_field_map = {
        "order_id": "pk",
        "date": "created_date",
        "balance": "balance",
    }

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
        context["dynamic_content"] = {
            "search_min_length": settings.DJANGO_DYNAMIC_CONTENT__SEARCH_MIN_LENGTH,
            "search_debounce_ms": settings.DJANGO_DYNAMIC_CONTENT__SEARCH_DEBOUNCE_MS,
            "orders_sync_interval_ms": settings.DJANGO_DYNAMIC_CONTENT__ORDERS_SYNC_INTERVAL_MS,
            "local_mutation_skip_ms": settings.DJANGO_DYNAMIC_CONTENT__LOCAL_MUTATION_SKIP_MS,
            "range_filter_debounce_ms": settings.DJANGO_DYNAMIC_CONTENT__RANGE_FILTER_DEBOUNCE_MS,
            "sync_highlight_ms": settings.DJANGO_DYNAMIC_CONTENT__SYNC_HIGHLIGHT_MS,
        }
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

    def get_sort_by(self):
        sort_by = (self.request.GET.get("sort_by") or "date").lower()
        if sort_by in self.allowed_sort_by:
            return sort_by
        return "date"

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

    def get_search_query(self):
        return (self.request.GET.get("q") or "").strip()

    def parse_optional_int(self, key):
        raw = self.request.GET.get(key)
        if raw is None or raw == "":
            return None
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None

    def parse_optional_decimal(self, key):
        raw = self.request.GET.get(key)
        if raw is None or raw == "":
            return None
        try:
            return Decimal(raw)
        except (InvalidOperation, TypeError, ValueError):
            return None

    def get_id_range(self):
        return self.parse_optional_int("id_min"), self.parse_optional_int("id_max")

    def get_balance_range(self):
        return (
            self.parse_optional_decimal("balance_min"),
            self.parse_optional_decimal("balance_max"),
        )

    def apply_ordering(self, queryset):
        sort_by = self.get_sort_by()
        sort = self.get_sort()
        field = self.sort_field_map[sort_by]
        prefix = "" if sort == "asc" else "-"
        if field == "pk":
            return queryset.order_by(f"{prefix}pk")
        return queryset.order_by(f"{prefix}{field}", f"{prefix}pk")

    def get_filtered_queryset(self):
        queryset = self.model.objects.for_list()
        queryset = queryset.of_types(*self.get_order_types())

        start_dt, end_dt = self.get_date_bounds()
        if start_dt is not None or end_dt is not None:
            queryset = queryset.created_between(start_dt, end_dt)

        id_min, id_max = self.get_id_range()
        if id_min is not None:
            queryset = queryset.filter(pk__gte=id_min)
        if id_max is not None:
            queryset = queryset.filter(pk__lte=id_max)

        balance_min, balance_max = self.get_balance_range()
        if balance_min is not None:
            queryset = queryset.filter(balance__gte=balance_min)
        if balance_max is not None:
            queryset = queryset.filter(balance__lte=balance_max)

        search_query = self.get_search_query()
        if len(search_query) >= 2:
            queryset = queryset.search_contains(search_query)

        return self.apply_ordering(queryset)

    def encode_cursor(self, order):
        sort_by = self.get_sort_by()
        if sort_by == "order_id":
            raw = str(order.pk)
        elif sort_by == "balance":
            raw = f"{order.balance}|{order.pk}"
        else:
            raw = f"{order.created_date.isoformat()}|{order.pk}"
        return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")

    def decode_cursor(self, cursor):
        sort_by = self.get_sort_by()
        try:
            raw = base64.urlsafe_b64decode(cursor.encode("ascii")).decode("utf-8")
            if sort_by == "order_id":
                return int(raw), None

            value_str, pk_str = raw.rsplit("|", 1)
            pk = int(pk_str)
            if sort_by == "balance":
                return Decimal(value_str), pk

            created_date = parse_datetime(value_str)
            if created_date is None:
                return None
            if timezone.is_naive(created_date):
                created_date = timezone.make_aware(created_date)
            return created_date, pk
        except (ValueError, InvalidOperation, TypeError):
            return None

    def apply_cursor(self, queryset, cursor, sort, sort_by):
        if not cursor:
            return queryset

        decoded = self.decode_cursor(cursor)
        if decoded is None:
            return queryset

        if sort_by == "order_id":
            pk, _ = decoded
            if sort == "asc":
                return queryset.filter(pk__gt=pk)
            return queryset.filter(pk__lt=pk)

        sort_value, pk = decoded
        field = self.sort_field_map[sort_by]
        if sort == "asc":
            return queryset.filter(
                Q(**{f"{field}__gt": sort_value})
                | Q(**{field: sort_value, "pk__gt": pk})
            )
        return queryset.filter(
            Q(**{f"{field}__lt": sort_value})
            | Q(**{field: sort_value, "pk__lt": pk})
        )

    def get_paginated_queryset(self, limit, cursor=None):
        sort = self.get_sort()
        sort_by = self.get_sort_by()
        queryset = self.apply_cursor(
            self.get_filtered_queryset(),
            cursor,
            sort,
            sort_by,
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

    def render_bounds_json_response(self):
        queryset = self.model.objects.for_list()
        aggregates = queryset.aggregate(
            id_min=Min("pk"),
            id_max=Max("pk"),
            balance_min=Min("balance"),
            balance_max=Max("balance"),
        )
        balance_min = aggregates["balance_min"]
        balance_max = aggregates["balance_max"]
        return JsonResponse(
            {
                "id_min": aggregates["id_min"] or 0,
                "id_max": aggregates["id_max"] or 0,
                "balance_min": float(balance_min if balance_min is not None else 0),
                "balance_max": float(balance_max if balance_max is not None else 0),
            }
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
                "watermark": self.get_sync_watermark(),
            }
        )

    def get_sync_watermark(self):
        """Server 'now' floored to UTC seconds, as microseconds.

        SQLite stores DateTime as second-precision strings. A fractional `since`
        such as 12:00:04.800 misses a row stored as 12:00:04. Flooring matches
        that storage so the query can be `updated_at >= since` with no lookback.
        """
        now = timezone.now()
        if timezone.is_naive(now):
            now = timezone.make_aware(now)
        return str(int(now.timestamp()) * 1_000_000)

    def parse_since(self):
        raw = (self.request.GET.get("since") or "").strip()
        if not raw:
            return None
        try:
            micros = int(raw)
            return datetime.fromtimestamp(micros / 1_000_000, tz=datetime_timezone.utc)
        except (TypeError, ValueError, OSError, OverflowError):
            pass
        parsed = parse_datetime(raw)
        if parsed is None:
            return None
        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed)
        return parsed

    def empty_sync_payload(self, watermark, reload=False):
        return {
            "watermark": watermark,
            "deleted_ids": [],
            "created_ids": [],
            "updated_ids": [],
            "rows_html": "",
            "reload": reload,
        }

    def render_sync_json_response(self):
        watermark = self.get_sync_watermark()
        since = self.parse_since()
        if since is None:
            return JsonResponse(self.empty_sync_payload(watermark))

        changed = list(
            self.model.objects.all_with_deleted()
            .filter(updated_at__gte=since)
            .only("pk", "deleted_at", "created_at", "updated_at")
        )
        if len(changed) > self.sync_delta_limit:
            return JsonResponse(self.empty_sync_payload(watermark, reload=True))
        if not changed:
            return JsonResponse(self.empty_sync_payload(watermark))

        deleted_ids = [row.pk for row in changed if row.deleted_at is not None]
        active_ids = [row.pk for row in changed if row.deleted_at is None]
        created_at_by_id = {row.pk: row.created_at for row in changed}

        matching_rows = []
        if active_ids:
            matching_rows = list(
                self.get_filtered_queryset().filter(pk__in=active_ids).distinct()
            )
        matching_id_set = {row.pk for row in matching_rows}
        deleted_ids.extend(pk for pk in active_ids if pk not in matching_id_set)

        created_ids = []
        updated_ids = []
        for row in matching_rows:
            created_at = created_at_by_id.get(row.pk)
            if created_at is not None and created_at > since:
                created_ids.append(row.pk)
            else:
                updated_ids.append(row.pk)

        return JsonResponse(
            {
                "watermark": watermark,
                "deleted_ids": deleted_ids,
                "created_ids": created_ids,
                "updated_ids": updated_ids,
                "rows_html": self.render_rows_html(matching_rows) if matching_rows else "",
                "reload": False,
            }
        )

    def get(self, request, *args, **kwargs):
        if self.model is not None and self.rows_template_name:
            if request.GET.get("bounds") == "1":
                return self.render_bounds_json_response()
            if request.GET.get("sync") == "1":
                return self.render_sync_json_response()
            return self.render_rows_json_response()
        return super().get(request, *args, **kwargs)
