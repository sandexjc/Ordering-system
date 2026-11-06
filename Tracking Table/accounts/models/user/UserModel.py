from django.contrib import auth
from django.db import models

from accounts.service import UserWorkflow
from common.mixins import WorkflowModelMixin


USER_ROLES = (
    ("Admin", "Администратор"),
    ("Store", "Магазин"),
    ("Warehouse", "Склад"),
    ("External", "Външен потребител"),
)


class User(auth.models.User, auth.models.PermissionsMixin, WorkflowModelMixin):

    """

    Hierarchy:
    auth.models.User -> User
    auth.models.PermissionsMixin -> User
    WorkflowModelMixin -> User

    --- Fields inherited from auth.models.User ---

    Inherits Django auth user fields.

    --- Fields inherited from auth.models.PermissionsMixin ---

    Inherits Django permissions fields.

    --- Fields inherited from WorkflowModelMixin ---

    workflow_service_class = BaseWorkflow

    --- Fields defined on User ---

    role = CharField(choices in USER_ROLES, default Store)
    password_reset_version = incremented on each set-password email so older links stop working

    """

    workflow_service_class = UserWorkflow

    role = models.CharField(
        max_length=32,
        choices=USER_ROLES,
        default="Store",
    )
    password_reset_version = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.first_name)
