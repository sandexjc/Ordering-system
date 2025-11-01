from django.utils import timezone
from .BaseQuerySet import BaseQuerySet

class BaseOrderQuerySet(BaseQuerySet):

    """ Queryset designed to share common Order models logic between apps. """

    # Load order related items 
    def with_items(self, *related_items):
        return self.prefetch_related(*related_items)
    
    # Telephone number orders filtering
    def telephone_contains(self, number):
        return self.filter(telephone__icontains=number)
    
    # Client name based orers filtering
    def owner_contains(self, name):
        return self.filter(owner__icontains=name)
    
    # Last created orders sorting
    def last_created(self):
        return self.order_by("-created_date")
    
    # First created orders sorting
    def first_created(self):
        return self.order_by("created_date")
    
    # Time based orders filtering 
    def most_recent(self, days):
        return self.filter(created_at__gte=timezone.now() - timezone.timedelta(days=days))

    # Period based orders filtering (start-end date)
    def created_between(self, start_date, end_date):
        return self.filter(created_date__range=(start_date, end_date))