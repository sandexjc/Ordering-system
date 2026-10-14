from django.conf import settings
from django.db import models
from django.utils import timezone

class BaseChange(models.Model):

    """

    Hierarchy:
    models.Model -> BaseChange

    --- Fields inherited from models.Model ---

    No explicit class fields inherited.

    """

    date = models.DateTimeField(default=timezone.now)
    user = models.CharField(max_length=100, default='N/A')
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_changes",
    )
    operation = models.CharField(max_length=100, default='N/A')
    related_item = models.CharField(max_length=100, default='N/A')
    field_label = models.CharField(max_length=100, blank=True, default='')
    current_state = models.CharField(max_length=500, default='')
    new_state = models.CharField(max_length=500, default='')

    class Meta:
        abstract = True