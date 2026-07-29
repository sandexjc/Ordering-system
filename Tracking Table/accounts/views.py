from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts import forms
from accounts.models import User


class CreateUser(LoginRequiredMixin, CreateView):

    """

    Hierarchy:
    LoginRequiredMixin -> CreateUser
    CreateView -> CreateUser

    --- Fields inherited from LoginRequiredMixin ---

    No explicit class fields inherited.

    --- Fields inherited from CreateView ---

    No explicit class fields inherited.

    """

    form_class = forms.UserCreateForm
    template_name = 'accounts/create-user.html'
    success_url = reverse_lazy('accounts:view-users')

class Login(LoginView):

    """

    Hierarchy:
    LoginView -> Login

    --- Fields inherited from LoginView ---

    No explicit class fields inherited.

    """

    form_class = forms.LoginForm
    template_name = 'accounts/login.html'
    next_page = '/'

class Logout(LoginRequiredMixin, LogoutView):

    """

    Hierarchy:
    LoginRequiredMixin -> Logout
    LogoutView -> Logout

    --- Fields inherited from LoginRequiredMixin ---

    No explicit class fields inherited.

    --- Fields inherited from LogoutView ---

    No explicit class fields inherited.

    """

    next_page = 'home'

class ViewUsers(LoginRequiredMixin, ListView):

    """

    Hierarchy:
    LoginRequiredMixin -> ViewUsers
    ListView -> ViewUsers

    --- Fields inherited from LoginRequiredMixin ---

    No explicit class fields inherited.

    --- Fields inherited from ListView ---

    No explicit class fields inherited.

    """

    model = User




