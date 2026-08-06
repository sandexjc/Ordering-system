from django.db.models import Q

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
            Q(owner__icontains=term)
            | Q(telephone__icontains=term)
            | Q(plates__material__icontains=term, plates__deleted_at__isnull=True)
            | Q(edges__edge_type__icontains=term, edges__deleted_at__isnull=True)
            | Q(edges__color_code__icontains=term, edges__deleted_at__isnull=True)
            | Q(notes__content__icontains=term, notes__deleted_at__isnull=True)
            | Q(others__description__icontains=term, others__deleted_at__isnull=True)
        ).distinct()
