from django.db.models import Q

from common.db import unicode_contains
from common.querysets import BaseOrderQuerySet


class VitrineOrderQuerySet(BaseOrderQuerySet):

    """
    Vitrine app domain level shared Vitrine models queryset.

    Hierarchy:
    models.QuerySet
        \
         -> BaseQuerySet -> BaseOrderQuerySet -> VitrineOrderQuerySet

    --- Fields inherited from BaseOrderQuerySet ---

    No explicit class fields inherited.

    """

    def order_type(self, order_type):
        return self.filter(order_type=order_type)

    # Partial match across vitrine + related item text fields
    def search_contains(self, query):
        term = (query or "").strip()
        if len(term) < 2:
            return self

        return self.filter(
            unicode_contains("owner", term)
            | unicode_contains("telephone", term)
            | Q(unicode_contains("frames__profile_type", term), frames__deleted_at__isnull=True)
            | Q(unicode_contains("frames__glass_type", term), frames__deleted_at__isnull=True)
            | Q(unicode_contains("notes__content", term), notes__deleted_at__isnull=True)
            | Q(unicode_contains("others__description", term), others__deleted_at__isnull=True)
        ).distinct()
