from django.contrib.auth.mixins import UserPassesTestMixin

from accounts.helpers.user_is_app_admin import user_is_app_admin


class AdminRequiredMixin(UserPassesTestMixin):

    """

    Hierarchy:
    UserPassesTestMixin -> AdminRequiredMixin

    Allows role Admin, or a Django superuser (always Admin, regardless of role).

    """

    def test_func(self):
        # Django UserPassesTestMixin requires this method name (not a unit test).
        return user_is_app_admin(self.request.user)
