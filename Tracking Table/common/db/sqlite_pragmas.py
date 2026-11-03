from django.db.backends.signals import connection_created


def configure_sqlite_pragmas(sender, connection, **kwargs):
    """
    Readers use WAL so a writer does not block them.
    busy_timeout matches OPTIONS['timeout'] (seconds): a locked writer
    raises after that wait instead of holding the request open.
    """
    if connection.vendor != "sqlite":
        return
    timeout_seconds = connection.settings_dict.get("OPTIONS", {}).get("timeout", 5)
    busy_ms = int(float(timeout_seconds) * 1000)
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA busy_timeout=%d" % busy_ms)
        cursor.execute("PRAGMA journal_mode=WAL")
        mode = cursor.fetchone()
    if mode and mode[0] not in ("wal", "memory"):
        raise RuntimeError("SQLite journal_mode stayed %s" % mode[0])


def connect_sqlite_pragmas():
    connection_created.connect(
        configure_sqlite_pragmas,
        dispatch_uid="common.db.sqlite_pragmas",
    )
