from django.contrib.auth.tokens import PasswordResetTokenGenerator

from accounts.models.User import User


class SetPasswordTokenGenerator(PasswordResetTokenGenerator):

    """

    Hierarchy:
    PasswordResetTokenGenerator -> SetPasswordTokenGenerator

    Includes accounts.User.password_reset_version so a new email
    invalidates every earlier link for that user.

    """

    def _make_hash_value(self, user, timestamp):
        login_timestamp = (
            ""
            if user.last_login is None
            else user.last_login.replace(microsecond=0, tzinfo=None)
        )
        email_field = user.get_email_field_name()
        email = getattr(user, email_field, "") or ""
        accounts_user = user if isinstance(user, User) else User.objects.filter(pk=user.pk).first()
        version = getattr(accounts_user, "password_reset_version", 0)
        return f"{user.pk}{user.password}{login_timestamp}{timestamp}{email}{version}"


SET_PASSWORD_TOKEN_GENERATOR = SetPasswordTokenGenerator()
