from django.conf import settings
from django.db import models
from django.utils import timezone


class Device(models.Model):

    """

    Hierarchy:
    models.Model -> Device

    One enrolled browser. The browser keeps the raw enrollment secret.
    This row keeps only that hash.

    A row with token_hash and no secret_hash is an activation link that
    has not been confirmed yet. activation_secret holds that link's raw
    token until the link is used, revoked, or replaced.

    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devices",
    )
    device_name = models.CharField(max_length=100, blank=True, default="")
    secret_hash = models.CharField(max_length=64, unique=True, null=True, blank=True)
    token_hash = models.CharField(max_length=64, unique=True, null=True, blank=True)
    activation_secret = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.device_name or "Device %s" % self.pk
