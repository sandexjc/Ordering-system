from django.utils import timezone
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
        return self.filter(telephone__icontains=number)
    
    # Client name based orers filtering
    def owner_contains(self, name):
        return self.filter(owner__icontains=name)

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
