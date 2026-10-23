from django.conf import settings
from django.db import models
from django.utils import timezone


class Device(models.Model):

    """

    Hierarchy:
    models.Model -> Device

    One enrolled browser secret for one user. The browser keeps the raw
    secret. This row keeps only the hash. A row with token_hash and no
    secret_hash is an emailed link that has not been confirmed yet.

    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devices",
    )
    device_name = models.CharField(max_length=100, blank=True, default="")
    secret_hash = models.CharField(max_length=64, unique=True, null=True, blank=True)
    token_hash = models.CharField(max_length=64, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.device_name or "Device %s" % self.pk
