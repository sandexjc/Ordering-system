from django.contrib.auth.models import User as AuthUser

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


def active_app_admin_count():
    admin_pks = set(
        User.objects.filter(is_active=True, role=USER_ROLE_ADMIN).values_list("pk", flat=True)
    )
    admin_pks.update(
        AuthUser.objects.filter(is_active=True, is_superuser=True).values_list("pk", flat=True)
    )
    return len(admin_pks)


def deactivate_blocked_reason(actor, target):
    if actor.pk == target.pk:
        return "Не можете да деактивирате собствения си профил."
    if target.is_active and user_is_app_admin(target) and active_app_admin_count() <= 1:
        return "Не можете да деактивирате последния администратор."
    return None
