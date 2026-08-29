from django.contrib.auth.mixins import UserPassesTestMixin

from accounts.constants import USER_ROLE_ADMIN
from accounts.models import User


class AdminRequiredMixin(UserPassesTestMixin):

    """

    Hierarchy:
    UserPassesTestMixin -> AdminRequiredMixin

    Allows role Admin, or a Django superuser (always Admin, regardless of role).

    """

    def test_func(self):
        # Django UserPassesTestMixin requires this method name (not a unit test).
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        accounts_user = User.objects.filter(pk=user.pk).first()
        if accounts_user is None:
            return False
        return accounts_user.role == USER_ROLE_ADMIN
