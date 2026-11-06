from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


DUPLICATE_EMAIL_MESSAGE = "Този имейл адрес вече се използва."


def normalize_email(email):
    return (email or "").strip()


def email_is_taken(email, exclude_pk=None):
    normalized = normalize_email(email)
    if not normalized:
        return False
    existing = get_user_model().objects.filter(email__iexact=normalized)
    if exclude_pk is not None:
        existing = existing.exclude(pk=exclude_pk)
    return existing.exists()


def validate_unique_email(email, exclude_pk=None):
    if email_is_taken(email, exclude_pk=exclude_pk):
        raise ValidationError(DUPLICATE_EMAIL_MESSAGE, code="unique")
