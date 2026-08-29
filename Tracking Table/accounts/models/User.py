from django.contrib import auth
from django.db import models

from accounts.constants import USER_ROLE_CHOICES, USER_ROLE_STORE


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

    """

    role = models.CharField(
        max_length=32,
        choices=USER_ROLE_CHOICES,
        default=USER_ROLE_STORE,
    )

    def __str__(self):
        return str(self.first_name)
