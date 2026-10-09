from django.db import models
from django.utils import timezone

from common.managers import BaseManager
from common.mixins import WorkflowModelMixin

class BaseModel(models.Model, WorkflowModelMixin):

    """

    Hierarchy:
    models.Model -> BaseModel
    WorkflowModelMixin -> BaseModel

    --- Fields inherited from models.Model ---

    No explicit class fields inherited.

    --- Fields inherited from WorkflowModelMixin ---

    workflow_service_class = BaseWorkflow

    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = BaseManager()

    class Meta:
        abstract = True
    
    def soft_delete(self):
        now = timezone.now()
        self.deleted_at = now
        self.updated_at = now
        self.save(update_fields=["deleted_at", "updated_at"])

    def restore(self):
        self.deleted_at = None
        self.updated_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])
