from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class MainView(LoginRequiredMixin, TemplateView):

    """

    Hierarchy:
    LoginRequiredMixin -> MainView
    TemplateView -> MainView

    --- Fields inherited from LoginRequiredMixin ---

    No explicit class fields inherited.

    --- Fields inherited from TemplateView ---

    No explicit class fields inherited.

    """
