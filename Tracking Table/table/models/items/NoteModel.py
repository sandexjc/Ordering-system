from common.models import BaseNote
from table.models import TableItem


class Note(TableItem, BaseNote):

    """

    Hierarchy:
    BaseModel -> TableItem -> Note
    BaseNote -> Note

    --- Fields inherited from BaseModel via TableItem ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    --- Fields inherited from TableItem ---

    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = TableItemManager()

    --- Fields inherited from BaseNote ---

    user = models.CharField(max_length=50, default='n/a')
    date = models.DateTimeField(default=timezone.now)
    content = models.TextField(max_length=500, blank=True)

    """

    def __str__(self):
        return f'User: {self.user} / Order ID: {self.order_id}'