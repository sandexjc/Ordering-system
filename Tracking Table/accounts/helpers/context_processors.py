from accounts.helpers.user_is_app_admin import user_is_app_admin


def accounts_roles(request):
    return {"is_app_admin": user_is_app_admin(request.user)}
