from django.db import models
from django.contrib import auth

class User(auth.models.User, auth.models.PermissionsMixin):

    """

    Hierarchy:
    auth.models.User -> User
    auth.models.PermissionsMixin -> User

    --- Fields inherited from auth.models.User ---

    Inherits Django auth user fields.

    --- Fields inherited from auth.models.PermissionsMixin ---

    Inherits Django permissions fields.

    """

    def __str__(self):
        return str(self.first_name)
        