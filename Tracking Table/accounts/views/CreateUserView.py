from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from accounts.forms import UserCreateForm
from accounts.helpers.send_set_password_email import send_set_password_email
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

    def form_valid(self, form):
        response = super().form_valid(form)
        try:
            sent = send_set_password_email(self.request, self.object)
        except Exception:
            messages.error(
                self.request,
                "Потребителят е създаден, но имейлът не беше изпратен.",
            )
            return response

        if sent:
            messages.success(
                self.request,
                "Потребителят е създаден. Изпратен е имейл за задаване на парола.",
            )
        else:
            messages.error(
                self.request,
                "Потребителят е създаден, но няма имейл адрес.",
            )
        return response
