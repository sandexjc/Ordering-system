from django.db import connection
from django.db.models import F, Q, Value
from django.db.models.lookups import Contains

from .sqlite_unicode import UnicodeLower


def unicode_contains(field_name, term):
    """
    Case-insensitive partial match for ``field_name``.

    On SQLite, Django's ``icontains`` is ASCII-only, so we compare both sides
    with Unicode case folding. Other backends keep ``icontains``.
    """
    if connection.vendor != "sqlite":
        return Q(**{f"{field_name}__icontains": term})

    folded = (term or "").casefold()
    return Q(Contains(UnicodeLower(F(field_name)), Value(folded)))
