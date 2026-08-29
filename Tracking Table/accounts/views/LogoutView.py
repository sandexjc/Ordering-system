from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView as DjangoLogoutView


class Logout(LoginRequiredMixin, DjangoLogoutView):

    """

    Hierarchy:
    LoginRequiredMixin -> Logout
    LogoutView -> Logout

    """

    next_page = "home"
