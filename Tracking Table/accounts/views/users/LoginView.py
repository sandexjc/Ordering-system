from django.conf import settings
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.forms.utils import ErrorDict

from accounts.forms import LoginForm
from accounts.helpers.devices.device_cookie import (
    DEVICE_LOGIN_MESSAGE,
    user_owns_cookie_device,
)
from accounts.helpers.users.login_rate_limit import (
    LOGIN_RATE_LIMIT_MESSAGE,
    clear_login_failures,
    login_is_locked,
    record_login_failure,
)


class Login(DjangoLoginView):

    """

    Hierarchy:
    LoginView -> Login

    """

    form_class = LoginForm
    template_name = "accounts/login.html"

    def post(self, request, *args, **kwargs):
        if login_is_locked(request):
            form = self.get_form()
            form.cleaned_data = {}
            form._errors = ErrorDict()
            form.add_error(None, LOGIN_RATE_LIMIT_MESSAGE)
            return self.render_to_response(self.get_context_data(form=form))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        if settings.DJANGO_FEATURES__BROWSER_COOKIE_FILTER and not user_owns_cookie_device(
            self.request, form.get_user()
        ):
            form.add_error(None, DEVICE_LOGIN_MESSAGE)
            return self.form_invalid(form)
        clear_login_failures(self.request)
        return super().form_valid(form)

    def form_invalid(self, form):
        record_login_failure(self.request)
        return super().form_invalid(form)
