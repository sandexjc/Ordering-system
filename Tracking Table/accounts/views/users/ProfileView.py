from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from accounts.forms import UserPreferenceForm, UserProfileForm
from accounts.models import UserPreference


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
        context["preference_form"] = UserPreferenceForm(
            initial={"theme": UserPreference.theme_for(self.request.user)}
        )
        context["browser_cookie_filter_enabled"] = settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER
        return context

    def form_valid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            form.save()
            return JsonResponse({"ok": True})
        messages.success(self.request, "Профилът е запазен.")
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False}, status=400)
        return super().form_invalid(form)
