from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from common.db import unicode_contains

from .BaseQuerySet import BaseQuerySet

class BaseOrderQuerySet(BaseQuerySet):

    """
    Queryset designed to share common Order models logic between apps.

    Hierarchy:
    models.QuerySet
        \
         -> BaseQuerySet -> BaseOrderQuerySet

    --- Fields inherited from BaseQuerySet ---

    No explicit class fields inherited.

    """

    # Load order related items 
    def with_items(self, *related_items):
        return self.prefetch_related(*related_items)
    
    # Telephone number orders filtering
    def telephone_contains(self, number):
        return self.filter(unicode_contains("telephone", number))
    
    # Client name based orers filtering
    def owner_contains(self, name):
        return self.filter(unicode_contains("owner", name))

    def pk_exact(self, term):
        """Exact order-id match when the term is a whole number."""
        if not str(term).isdecimal():
            return Q()
        return Q(pk=int(term))

    def related_text_exists(self, related_name, term, *field_names):
        """Match related rows with EXISTS instead of JOIN.

        OR-search across several item tables must not JOIN them all at once;
        that multiplies rows (orders × plates × edges × notes) and makes
        UNICODE_LOWER scans unusable on large SQLite databases.
        """
        if not field_names:
            raise ValueError("related_text_exists requires at least one field name.")
        rel = self.model._meta.get_field(related_name)
        match = Q()
        for name in field_names:
            match |= unicode_contains(name, term)
        return Exists(
            rel.related_model.objects.filter(
                **{rel.field.name: OuterRef("pk")},
                deleted_at__isnull=True,
            ).filter(match)
        )

    # Filter by one or more order types (order/offer). Empty → no rows.
    def of_types(self, *order_types):
        types = [value for value in order_types if value]
        if not types:
            return self.none()
        if len(types) == 1:
            return self.filter(order_type=types[0])
        return self.filter(order_type__in=types)
    
    # Last created orders sorting
    def last_created(self):
        return self.order_by("-created_date", "-pk")
    
    # First created orders sorting
    def first_created(self):
        return self.order_by("created_date", "pk")
    
    # Time based orders filtering 
    def most_recent(self, days):
        return self.filter(created_date__gte=timezone.now() - timezone.timedelta(days=days))

    # Period based orders filtering (start and/or end date)
    def created_between(self, start_date=None, end_date=None):
        queryset = self
        if start_date is not None:
            queryset = queryset.filter(created_date__gte=start_date)
        if end_date is not None:
            queryset = queryset.filter(created_date__lte=end_date)
        return queryset
