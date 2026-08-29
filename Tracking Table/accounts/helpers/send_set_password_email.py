from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.helpers.set_password_token_generator import SET_PASSWORD_TOKEN_GENERATOR


class SetPasswordEmailMessage(EmailMessage):

    """

    Hierarchy:
    EmailMessage -> SetPasswordEmailMessage

    Django adds Message-ID automatically. That header is only for mail
    clients/servers; the set-password token does not use it.

    """

    def message(self):
        msg = super().message()
        del msg["Message-ID"]
        return msg


def send_set_password_email(request, user):
    if not user.email:
        return False

    user.password_reset_version += 1
    user.save(update_fields=["password_reset_version"])

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = SET_PASSWORD_TOKEN_GENERATOR.make_token(user)
    path = reverse(
        "accounts:set-password",
        kwargs={"uidb64": uid, "token": token},
    )
    set_password_url = request.build_absolute_uri(path)
    display_name = user.first_name or user.username
    subject = "Активиране на потребителски акаунт"
    body = render_to_string(
        "accounts/email/set_password.txt",
        {
            "display_name": display_name,
            "email_from_address": settings.EMAIL_FROM_ADDRESS,
            "set_password_url": set_password_url,
            "link_valid_minutes": settings.PASSWORD_RESET_TIMEOUT // 60,
        },
    )
    email = SetPasswordEmailMessage(
        subject,
        body,
        settings.EMAIL_FROM_ADDRESS,
        [user.email],
    )
    email.send(fail_silently=False)
    return True
