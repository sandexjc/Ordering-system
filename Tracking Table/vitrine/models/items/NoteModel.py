from common.models import BaseNote
from vitrine.models.base import VitrineItem


class Note(VitrineItem, BaseNote):

    """

    Hierarchy:
    BaseModel -> VitrineItem -> Note
    BaseNote -> Note

    --- Fields inherited from BaseModel via VitrineItem ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    --- Fields inherited from VitrineItem ---

    vitrine_id = models.ForeignKey(Vitrine, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = VitrineItemManager()

    --- Fields inherited from BaseNote ---

    user = models.CharField(max_length=50, default='n/a')
    date = models.DateTimeField(default=timezone.now)
    content = models.TextField(max_length=500, blank=True)

    """

    def __str__(self):
        return f'User: {self.user} / Vitrine ID: {self.vitrine_id}'