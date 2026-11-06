from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from accounts.forms import UserPreferenceForm, UserProfileForm
from accounts.models import User, UserPreference
from accounts.service import UserWorkflow


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
        accounts_user = User.objects.filter(pk=self.request.user.pk).first()
        return accounts_user or self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_form"] = context["form"]
        saved = UserPreference.appearance_for(self.request.user)
        context["preference_form"] = UserPreferenceForm(initial=saved)
        context["browser_cookie_filter_enabled"] = settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        try:
            if isinstance(self.object, User):
                self.object.run_workflow_save()
            else:
                UserWorkflow.run_save_seq(self.object)
        except ValidationError as exc:
            form.add_error("email", exc.message_dict.get("email", exc.messages))
            return self.form_invalid(form)
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(self.request, "Профилът е запазен.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            message = "Профилът не беше запазен."
            if form.errors:
                message = next(iter(form.errors.values()))[0]
            return JsonResponse({"ok": False, "error": message}, status=400)
        return super().form_invalid(form)
