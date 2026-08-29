from accounts.helpers.constants import USER_ROLE_ADMIN
from accounts.models.User import User


def user_is_app_admin(user):
    if not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True
    accounts_user = User.objects.filter(pk=user.pk).first()
    if accounts_user is None:
        return False
    return accounts_user.role == USER_ROLE_ADMIN
