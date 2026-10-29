from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views import View

from accounts.forms import UserPreferenceForm
from accounts.models import UserPreference


class AppearancePreference(LoginRequiredMixin, View):

    """

    Hierarchy:
    LoginRequiredMixin -> AppearancePreference
    View -> AppearancePreference

    Saves the logged-in account's appearance row. Does not create a row
    until this post succeeds, and never writes another account.

    """

    def post(self, request):
        form = UserPreferenceForm(request.POST)
        ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        if not form.is_valid():
            if ajax:
                return JsonResponse({"ok": False}, status=400)
            messages.error(request, "Настройките не бяха запазени.")
            return redirect("accounts:profile")
        preference, _created = UserPreference.objects.get_or_create(user=request.user)
        preference.theme = form.cleaned_data["theme"]
        preference.background = form.cleaned_data["background"]
        preference.accent = form.cleaned_data["accent"]
        preference.text_size = form.cleaned_data["text_size"]
        preference.row_density = form.cleaned_data["row_density"]
        preference.reduced_motion = form.cleaned_data["reduced_motion"]
        preference.save(update_fields=["theme", "background", "accent", "text_size", "row_density", "reduced_motion"])
        if ajax:
            return JsonResponse({"ok": True})
        messages.success(request, "Настройките за външен вид са запазени.")
        return redirect("accounts:profile")
