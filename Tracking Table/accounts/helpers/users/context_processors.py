from accounts.helpers.users.user_is_app_admin import user_is_app_admin
from accounts.models import UserPreference


def accounts_roles(request):
    return {"is_app_admin": user_is_app_admin(request.user)}


def appearance(request):
    return {"appearance_theme": UserPreference.theme_for(request.user)}
