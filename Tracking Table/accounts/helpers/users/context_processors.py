from accounts.helpers.users.user_is_app_admin import user_is_app_admin
from accounts.models import UserPreference


def accounts_roles(request):
    return {"is_app_admin": user_is_app_admin(request.user)}


def appearance(request):
    saved = UserPreference.appearance_for(request.user)
    return {
        "appearance_theme": saved["theme"],
        "appearance_background": saved["background"],
        "appearance_accent": saved["accent"],
        "appearance_text_size": saved["text_size"],
        "appearance_row_density": saved["row_density"],
        "appearance_reduced_motion": saved["reduced_motion"],
    }
