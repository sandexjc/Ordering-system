from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.helpers.set_password_token_generator import SET_PASSWORD_TOKEN_GENERATOR
from accounts.models.User import User as AccountsUser

ACTIVATION_EMAIL_SUBJECT = "Активиране на потребителски акаунт"
ACTIVATION_EMAIL_TEMPLATE = "accounts/email/set_password.txt"
CHANGE_PASSWORD_EMAIL_SUBJECT = "Смяна на парола"
CHANGE_PASSWORD_EMAIL_TEMPLATE = "accounts/email/change_password.txt"


class SetPasswordEmailMessage(EmailMultiAlternatives):

    """

    Hierarchy:
    EmailMultiAlternatives -> SetPasswordEmailMessage

    Django adds Message-ID automatically. That header is only for mail
    clients/servers; the set-password token does not use it.

    """

    def message(self):
        msg = super().message()
        del msg["Message-ID"]
        return msg


def send_set_password_email(
    request,
    user,
    *,
    subject=ACTIVATION_EMAIL_SUBJECT,
    email_template=ACTIVATION_EMAIL_TEMPLATE,
):
    if not user.email:
        return False

    accounts_user = (
        user
        if isinstance(user, AccountsUser)
        else AccountsUser.objects.filter(pk=user.pk).first()
    )
    token_user = accounts_user or user
    if accounts_user is not None:
        accounts_user.password_reset_version += 1
        accounts_user.save(update_fields=["password_reset_version"])
        token_user = accounts_user

    uid = urlsafe_base64_encode(force_bytes(token_user.pk))
    token = SET_PASSWORD_TOKEN_GENERATOR.make_token(token_user)
    path = reverse(
        "accounts:set-password",
        kwargs={"uidb64": uid, "token": token},
    )
    set_password_url = request.build_absolute_uri(path)
    display_name = token_user.first_name or token_user.username
    context = {
        "display_name": display_name,
        "username": token_user.username,
        "email_from_address": settings.EMAIL_FROM_ADDRESS,
        "set_password_url": set_password_url,
        "link_valid_minutes": settings.PASSWORD_RESET_TIMEOUT // 60,
    }
    body = render_to_string(email_template, context)
    html_body = render_to_string(email_template.replace(".txt", ".html"), context)
    email = SetPasswordEmailMessage(
        subject,
        body,
        settings.EMAIL_FROM_ADDRESS,
        [token_user.email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
    return True
