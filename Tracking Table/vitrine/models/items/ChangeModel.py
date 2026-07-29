from common.models import BaseChange
from vitrine.models.base import VitrineItem

class Change(VitrineItem, BaseChange):

    """

    Hierarchy:
    BaseModel -> VitrineItem -> Change
    BaseChange -> Change

    --- Fields inherited from BaseModel via VitrineItem ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    --- Fields inherited from VitrineItem ---

    vitrine_id = models.ForeignKey(Vitrine, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = VitrineItemManager()

    --- Fields inherited from BaseChange ---

    date = models.DateTimeField(default=timezone.now)
    user = models.CharField(max_length=100, default='N/A')
    operation = models.CharField(max_length=100, default='N/A')
    related_item = models.CharField(max_length=100, default='N/A')
    current_state = models.CharField(max_length=100, default='')
    new_state = models.CharField(max_length=100, default='')

    """

    def __str__(self):
        return f'User: {self.user} / Order ID: {self.vitrine_id}'