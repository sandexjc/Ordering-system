from django.db import models
from django.utils import timezone
from common.managers import BaseManager
from common.signals import soft_deleted, restored

class BaseModel(models.Model):
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = BaseManager()

    class Meta:
        abstract = True
    
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])
        # send deleted signal
        soft_deleted.send(sender=self.__class__, instance=self)

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])
        # send restored signal
        restored.send(sender=self.__class__, instance=self)
