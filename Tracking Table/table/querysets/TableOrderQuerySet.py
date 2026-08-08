from django.db.models import Q

from common.db import unicode_contains
from common.querysets import BaseOrderQuerySet


class TableOrderQuerySet(BaseOrderQuerySet):

    """
    Table app domain level shared Order models queryset.

    Hierarchy:
    models.QuerySet
        \
         -> BaseQuerySet -> BaseOrderQuerySet -> TableOrderQuerySet

    --- Fields inherited from BaseOrderQuerySet ---

    No explicit class fields inherited.

    """

    # Order type filtering (order/offer)
    def order_type(self, order_type):
        return self.filter(order_type=order_type)

    # Partial match across order + related item text fields
    def search_contains(self, query):
        term = (query or "").strip()
        if len(term) < 2:
            return self

        return self.filter(
            unicode_contains("owner", term)
            | unicode_contains("telephone", term)
            | Q(unicode_contains("plates__material", term), plates__deleted_at__isnull=True)
            | Q(unicode_contains("edges__edge_type", term), edges__deleted_at__isnull=True)
            | Q(unicode_contains("edges__color_code", term), edges__deleted_at__isnull=True)
            | Q(unicode_contains("notes__content", term), notes__deleted_at__isnull=True)
            | Q(unicode_contains("others__description", term), others__deleted_at__isnull=True)
        ).distinct()
