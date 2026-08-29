from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import UserCreateForm
from accounts.mixins import AdminRequiredMixin


class CreateUser(AdminRequiredMixin, CreateView):

    """

    Hierarchy:
    AdminRequiredMixin -> CreateUser
    CreateView -> CreateUser

    """

    form_class = UserCreateForm
    template_name = "accounts/create-user.html"
    success_url = reverse_lazy("accounts:view-users")
