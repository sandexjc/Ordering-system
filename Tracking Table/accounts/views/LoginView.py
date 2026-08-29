from django.contrib.auth.views import LoginView as DjangoLoginView

from accounts.forms import LoginForm


class Login(DjangoLoginView):

    """

    Hierarchy:
    LoginView -> Login

    """

    form_class = LoginForm
    template_name = "accounts/login.html"
    next_page = "/"
