from django.db.backends.signals import connection_created
from django.db.models import CharField, Func


def _unicode_casefold(value):
    if value is None:
        return None
    return str(value).casefold()


def register_sqlite_unicode_lower(sender, connection, **kwargs):
    """
    SQLite LOWER()/LIKE only fold ASCII. Register a Python casefold() so
    Cyrillic (and other non-ASCII) search can be case-insensitive.
    """
    if connection.vendor != "sqlite":
        return
    connection.connection.create_function(
        "UNICODE_LOWER",
        1,
        _unicode_casefold,
        deterministic=True,
    )


def connect_sqlite_unicode_lower():
    connection_created.connect(register_sqlite_unicode_lower)


class UnicodeLower(Func):
    """Case-fold expression; uses UNICODE_LOWER on SQLite, LOWER elsewhere."""

    arity = 1
    output_field = CharField()

    def as_sqlite(self, compiler, connection, **extra_context):
        return self.as_sql(
            compiler,
            connection,
            function="UNICODE_LOWER",
            **extra_context,
        )

    def as_sql(self, compiler, connection, **extra_context):
        extra_context.setdefault("function", "LOWER")
        return super().as_sql(compiler, connection, **extra_context)
