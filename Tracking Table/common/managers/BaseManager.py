from django.db import models
from common.querysets import BaseQuerySet

class BaseManager(models.Manager):

    """ Top level Manager designed to share common models logic. """

    # Return active only objects
    def __get_queryset(self):
        return BaseQuerySet(self.model, using=self._db).active()

    # Return all objects including soft-deleted
    def all_with_deleted(self):
        return BaseQuerySet(self.model, using=self._db)

    # Return soft-deleted only objects
    def deleted(self):
        return self.all_with_deleted().deleted()