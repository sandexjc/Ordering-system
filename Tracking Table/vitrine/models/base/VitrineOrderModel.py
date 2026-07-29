from common.models import BaseModel
from vitrine.managers import VitrineOrderManager

class VitrineOrder(BaseModel):

    """

    Hierarchy:
    BaseModel -> VitrineOrder

    --- Fields inherited from BaseModel ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    """

    objects = VitrineOrderManager()

    class Meta:
        abstract = True