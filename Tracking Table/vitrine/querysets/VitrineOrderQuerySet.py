from django.db.models import Q

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
            Q(owner__icontains=term)
            | Q(telephone__icontains=term)
            | Q(frames__profile_type__icontains=term, frames__deleted_at__isnull=True)
            | Q(frames__glass_type__icontains=term, frames__deleted_at__isnull=True)
            | Q(notes__content__icontains=term, notes__deleted_at__isnull=True)
            | Q(others__description__icontains=term, others__deleted_at__isnull=True)
        ).distinct()
