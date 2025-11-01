from django.db import models
from django.utils import timezone

class BaseQuerySet(models.QuerySet):

    """ Top level QuerySet designed to share common logic for all models. """

    # Return only active objects
    def active(self):
        return self.filter(deleted_at__isnull=True)

    # Return only soft-deleted objects.
    def deleted(self):
        return self.exclude(deleted_at__isnull=True)

    # Permanently delete records.
    def hard_delete(self):
        return super().delete()

    # Soft delete all records in this queryset.
    def soft_delete(self):
        return self.update(deleted_at=timezone.now())