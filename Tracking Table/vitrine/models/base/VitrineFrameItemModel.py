from django.db import models

from common.models import BaseItem
from vitrine.service import BaseVitrineItemWorkflow
from vitrine.managers import VitrineFrameItemManager
from vitrine.models.items.FrameModel import Frame

class VitrineFrameItem(BaseItem):

    # Service layer workflow model speific functionality
    workflow_service_class = BaseVitrineItemWorkflow

    frame_id = models.ForeignKey(Frame, on_delete=models.CASCADE, related_name="%(class)ss")
    frame_objects = VitrineFrameItemManager()

    class Meta:
        abstract = True