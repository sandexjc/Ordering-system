from django.utils import timezone

from accounts.models import Device


def enrolled_devices(user_id):
    return Device.objects.filter(
        user_id=user_id,
        revoked_at__isnull=True,
        secret_hash__isnull=False,
    ).order_by("-created_at")


def device_list_item(device, revoke_url):
    return {
        "id": device.pk,
        "device_name": device.device_name or ("Устройство %s" % device.pk),
        "created_at": _format_timestamp(device.created_at),
        "last_used_at": _format_timestamp(device.last_used_at),
        "revoke_url": revoke_url,
    }


def _format_timestamp(value):
    if value is None:
        return ""
    return timezone.localtime(value).strftime("%d/%m/%Y %H:%M")
