from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts import forms
from accounts.models import User


class CreateUser(LoginRequiredMixin, CreateView):
    form_class = forms.UserCreateForm
    template_name = 'accounts/createUser.html'
    success_url = reverse_lazy('accounts:viewUsers')

class Login(LoginView):
    form_class = forms.LoginForm
    template_name = 'accounts/login.html'
    next_page = '/'

class Logout(LoginRequiredMixin, LogoutView):
    next_page = 'home'

class ViewUsers(LoginRequiredMixin, ListView):
    model = User




