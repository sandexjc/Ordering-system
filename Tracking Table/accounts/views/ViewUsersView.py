from django.views.generic import ListView

from accounts.mixins import AdminRequiredMixin
from accounts.models import User


class ViewUsers(AdminRequiredMixin, ListView):

    """

    Hierarchy:
    AdminRequiredMixin -> ViewUsers
    ListView -> ViewUsers

    """

    model = User
