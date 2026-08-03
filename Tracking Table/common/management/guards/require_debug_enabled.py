from django.conf import settings
from django.core.management.base import CommandError


def require_debug_enabled(command_name=None):
    """
    Block destructive/demo management commands unless DJANGO_DEBUG is True.

    Commands stay tracked in git for all branches; production simply cannot run them.
    """
    if settings.DEBUG:
        return

    label = command_name or "This command"
    raise CommandError(
        f"{label} is only available when DJANGO_DEBUG=True "
        f"(current DJANGO_ENVIRONMENT={getattr(settings, 'DJANGO_ENVIRONMENT', 'unknown')})."
    )
