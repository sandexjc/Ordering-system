from django.contrib import auth
from django.db import models

from accounts.helpers.constants import USER_ROLE_CHOICES, USER_ROLE_STORE


class User(auth.models.User, auth.models.PermissionsMixin):

    """

    Hierarchy:
    auth.models.User -> User
    auth.models.PermissionsMixin -> User

    --- Fields inherited from auth.models.User ---

    Inherits Django auth user fields.

    --- Fields inherited from auth.models.PermissionsMixin ---

    Inherits Django permissions fields.

    --- Fields defined on User ---

    role = CharField(choices Admin/Store/Warehouse/External, default Store)
    password_reset_version = incremented on each set-password email so older links stop working

    """

    role = models.CharField(
        max_length=32,
        choices=USER_ROLE_CHOICES,
        default=USER_ROLE_STORE,
    )
    password_reset_version = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.first_name)
