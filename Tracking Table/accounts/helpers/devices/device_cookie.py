import hashlib
import secrets

from django.conf import settings
from django.utils import timezone

from accounts.models import Device


COOKIE_NAME = "browser_devices"
EXEMPT_URL_NAMES = frozenset({"set-password", "activate-device"})
DEVICE_LOGIN_MESSAGE = "Това устройство не е активирано за този потребител."


def hash_secret(raw_secret):
    return hashlib.sha256(raw_secret.encode("utf-8")).hexdigest()


def read_secrets(request):
    raw_cookie = request.COOKIES.get(COOKIE_NAME, "")
    secrets_in_cookie = [part for part in raw_cookie.split(".") if part]
    return secrets_in_cookie[: settings.DJANGO_DEVICE_COOKIE__MAX_SECRETS]


def matching_active_devices(request):
    secret_hashes = [hash_secret(raw_secret) for raw_secret in read_secrets(request)]
    if not secret_hashes:
        return Device.objects.none()
    return Device.objects.filter(
        secret_hash__in=secret_hashes,
        revoked_at__isnull=True,
    )


def cookie_has_active_device(request):
    return matching_active_devices(request).exists()


def user_owns_cookie_device(request, user):
    return matching_active_devices(request).filter(user_id=user.pk).exists()


def touch_active_devices(request):
    matching_active_devices(request).update(last_used_at=timezone.now())


def _cookie_kwargs():
    return {
        "max_age": settings.DJANGO_DEVICE_COOKIE__MAX_AGE,
        "httponly": True,
        "secure": bool(settings.DJANGO_SECURITY_ENABLE),
        "samesite": "Strict",
        "path": "/",
    }


def write_secrets(request, response, raw_secrets):
    kept = [
        raw_secret
        for raw_secret in raw_secrets
        if raw_secret
    ][: settings.DJANGO_DEVICE_COOKIE__MAX_SECRETS]
    if not kept:
        response.delete_cookie(
            COOKIE_NAME,
            path="/",
            samesite="Strict",
            secure=bool(settings.DJANGO_SECURITY_ENABLE),
        )
        request.COOKIES.pop(COOKIE_NAME, None)
        return response
    cookie_value = ".".join(kept)
    response.set_cookie(COOKIE_NAME, cookie_value, **_cookie_kwargs())
    request.COOKIES[COOKIE_NAME] = cookie_value
    return response


def enroll_device(request, response, device):
    raw_secret = secrets.token_urlsafe(32)
    device.secret_hash = hash_secret(raw_secret)
    device.token_hash = None
    device.last_used_at = timezone.now()
    device.save()
    write_secrets(request, response, read_secrets(request) + [raw_secret])
    return device


def append_device(request, response, user, device_name=""):
    device = Device(user=user, device_name=device_name or "")
    return enroll_device(request, response, device)


def revoke_device(request, response, device):
    if device.revoked_at is None:
        device.revoked_at = timezone.now()
        device.save(update_fields=["revoked_at"])
    kept = [
        raw_secret
        for raw_secret in read_secrets(request)
        if hash_secret(raw_secret) != device.secret_hash
    ]
    write_secrets(request, response, kept)
    return device
