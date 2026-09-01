from django.views.generic import ListView

from accounts.helpers.constants import USER_ROLE_CHOICES
from accounts.helpers.user_is_app_admin import (
    deactivate_blocked_reason,
    role_change_blocked_reason,
)
from accounts.mixins import AdminRequiredMixin
from accounts.models import User


class ViewUsers(AdminRequiredMixin, ListView):

    """

    Hierarchy:
    AdminRequiredMixin -> ViewUsers
    ListView -> ViewUsers

    """

    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        actor = self.request.user
        context["role_choices"] = USER_ROLE_CHOICES
        for listed_user in context["user_list"]:
            listed_user.deactivate_block = deactivate_blocked_reason(actor, listed_user)
            listed_user.role_block = role_change_blocked_reason(actor, listed_user)
        return context
