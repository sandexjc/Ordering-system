from django.contrib.auth.models import User as AuthUser

from accounts.helpers.constants import USER_ROLE_ADMIN, USER_ROLES
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


def role_change_blocked_reason(actor, target, new_role=None):
    if actor.pk == target.pk:
        return "Не можете да промените собствената си група."
    if new_role is not None and new_role not in USER_ROLES:
        return "Невалидна група."
    demoting_last_admin = (
        target.role == USER_ROLE_ADMIN
        and not target.is_superuser
        and active_app_admin_count() <= 1
        and (new_role is None or new_role != USER_ROLE_ADMIN)
    )
    if demoting_last_admin:
        return "Не можете да премахнете групата на последния администратор."
    return None
