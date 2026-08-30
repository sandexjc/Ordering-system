from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from accounts.forms import UserProfileForm


class Profile(LoginRequiredMixin, UpdateView):

    """

    Hierarchy:
    LoginRequiredMixin -> Profile
    UpdateView -> Profile

    Logged-in user edits names and email. Password is changed via
    emailed one-time link, not a form on this page.

    """

    model = get_user_model()
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_form"] = context["form"]
        return context

    def form_valid(self, form):
        messages.success(self.request, "Профилът е запазен.")
        return super().form_valid(form)
