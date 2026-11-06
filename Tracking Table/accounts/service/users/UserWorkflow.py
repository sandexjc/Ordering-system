from django.core.exceptions import ValidationError

from accounts.helpers.users.unique_email import normalize_email, validate_unique_email
from common.service import BaseWorkflow


class UserWorkflow(BaseWorkflow):

    @classmethod
    def pre_save(cls, user):
        user.email = normalize_email(user.email)
        try:
            validate_unique_email(user.email, exclude_pk=user.pk)
        except ValidationError as exc:
            raise ValidationError({"email": exc.messages}) from exc
