import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from accounts.helpers.devices.device_cookie import hash_secret
from accounts.helpers.users.send_set_password_email import SetPasswordEmailMessage
from accounts.models import Device

DEVICE_ACTIVATION_EMAIL_SUBJECT = "Добавяне на устройство"
DEVICE_ACTIVATION_EMAIL_TEMPLATE = "accounts/email/add_device.txt"


def send_device_activation_email(request, user, device_name=""):
    if not settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER:
        return False
    if not getattr(user, "email", ""):
        return False

    Device.objects.filter(
        user_id=user.pk,
        secret_hash__isnull=True,
        revoked_at__isnull=True,
    ).update(revoked_at=timezone.now())
    raw_token = secrets.token_urlsafe(32)
    device = Device.objects.create(
        user=user,
        token_hash=hash_secret(raw_token),
        device_name=(device_name or "")[:100],
    )
    uid = urlsafe_base64_encode(force_bytes(device.pk))
    path = reverse(
        "accounts:activate-device",
        kwargs={"uidb64": uid, "token": raw_token},
    )
    context = {
        "display_name": user.first_name or user.username,
        "username": user.username,
        "email_from_address": settings.EMAIL_FROM_ADDRESS,
        "activate_device_url": request.build_absolute_uri(path),
        "device_name": device.device_name,
        "link_valid_minutes": settings.PASSWORD_RESET_TIMEOUT // 60,
    }
    body = render_to_string(DEVICE_ACTIVATION_EMAIL_TEMPLATE, context)
    html_body = render_to_string(
        DEVICE_ACTIVATION_EMAIL_TEMPLATE.replace(".txt", ".html"),
        context,
    )
    email = SetPasswordEmailMessage(
        DEVICE_ACTIVATION_EMAIL_SUBJECT,
        body,
        settings.EMAIL_FROM_ADDRESS,
        [user.email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
    return True


def activation_from_link(uidb64, token):
    try:
        activation_pk = force_str(urlsafe_base64_decode(uidb64))
        device = Device.objects.get(pk=activation_pk)
    except (
        Device.DoesNotExist,
        TypeError,
        ValueError,
        OverflowError,
    ):
        return None
    if device.secret_hash or device.revoked_at is not None or not device.token_hash:
        return None
    if not hmac.compare_digest(hash_secret(token), device.token_hash):
        return None
    expires_at = device.created_at + timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
    if timezone.now() > expires_at:
        return None
    return device
