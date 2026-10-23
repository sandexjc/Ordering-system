from django.http import Http404
from django.shortcuts import get_object_or_404

from accounts.helpers.users.user_is_app_admin import user_is_app_admin
from accounts.models import User


def device_subject(request, user_pk=None):
    if user_pk is None:
        return request.user
    if not user_is_app_admin(request.user):
        raise Http404()
    return get_object_or_404(User, pk=user_pk)
