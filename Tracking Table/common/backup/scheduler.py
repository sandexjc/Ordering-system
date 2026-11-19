import os
import sys
import threading
import time
import traceback
from datetime import timedelta

from django.conf import settings
from django.db import connection
from django.utils import timezone

from common.backup.export_backup import export_backup


# Held while checking _started, so two callers cannot both start a thread.
_start_lock = threading.Lock()

# True after this process has started the daily export thread.
_started = False


def server_process(argv=None, environ=None):
    # True when Passenger loaded this process through passenger_wsgi.py.
    # runserver and management commands do not own the daily export.
    argv = sys.argv if argv is None else argv
    environ = os.environ if environ is None else environ
    if environ.get("_ORDERING_WSGI_SERVER") == "1":
        return True
    script = os.path.basename(argv[0]) if argv else ""
    return script == "passenger_wsgi.py"


def next_backup_at(now):
    # Next local DJANGO_BACKUP_AT. A time already passed today waits until tomorrow.
    hour, minute = (int(part) for part in settings.DJANGO_BACKUP_AT.split(":"))
    if now > _at_clock(now, hour, minute):
        now = now + timedelta(days=1)
    return _at_clock(now, hour, minute)


def start_backup_scheduler():
    # Start the daily export thread once in the Passenger process.
    global _started

    if not server_process():
        return
    if not settings.DJANGO_FEATURES__DB_BACKUP:
        return
    if not settings.DJANGO_BACKUP_DIR:
        _report("Database backup is on, but DJANGO_BACKUP_DIR is unset. The daily export will not run.")
        return

    with _start_lock:
        if _started:
            return
        _started = True

    thread = threading.Thread(target=_backup_loop, name="database-backup", daemon=True)
    thread.start()


def _backup_loop():
    while True:
        _sleep_until(next_backup_at(timezone.localtime()))
        _export_once()


def _sleep_until(target):
    # Sleep until target. A second sleep happens only if the first returns early.
    while True:
        remaining = (target - timezone.localtime()).total_seconds()
        if remaining <= 0:
            return
        time.sleep(remaining)


def _export_once():
    try:
        result = export_backup(force=False)
    except Exception:
        _report("Database backup failed.")
        traceback.print_exc()
        return
    finally:
        connection.close()

    if result.written:
        _report(f"Database backup wrote {result.path}.")
    else:
        _report(f"Database backup skipped {result.path}; today's file already exists.")
    for path in result.removed:
        _report(f"Database backup removed {path.name}.")


def _at_clock(moment, hour, minute):
    return moment.replace(hour=hour, minute=minute, second=0, microsecond=0)


def _report(message):
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()
