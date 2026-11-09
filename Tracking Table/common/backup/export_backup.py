import fcntl
import os
import re
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.utils import timezone


# migrate recreates these, and their primary keys change on a new database.
DUMP_LABELS = (
    "auth.user",
    "auth.group",
    "accounts",
    "table",
    "vitrine",
)
DUMP_EXCLUDES = (
    "contenttypes",
    "auth.permission",
    "sessions",
    "admin.logentry",
)
BACKUP_FILE_NAME = re.compile(r"^backup-(\d{4}-\d{2}-\d{2})\.json$")


class BackupError(Exception):
    """The backup settings or file do not allow this operation."""


@dataclass(frozen=True)
class ExportResult:
    path: Path
    written: bool
    removed: tuple[Path, ...]


def export_backup(*, force=False):
    """
    Write today's JSON backup into DJANGO_BACKUP_DIR.

    Skips the write when that file already exists unless force is set.
    Removes daily files dated before the retention window.
    """
    backup_dir = backup_directory()
    today = timezone.localdate()
    destination = backup_dir / f"backup-{today.isoformat()}.json"

    with backup_lock(backup_dir):
        written = _write_dump(destination, force=force)
        removed = _remove_old_files(backup_dir, today, settings.DJANGO_BACKUP_KEEP_DAYS)

    return ExportResult(path=destination, written=written, removed=removed)


def backup_directory():
    if not settings.DJANGO_FEATURES__DB_BACKUP:
        raise BackupError("Database backup is off. Set DJANGO_FEATURES__DB_BACKUP=True.")

    backup_dir = settings.DJANGO_BACKUP_DIR
    if not backup_dir:
        raise BackupError("Database backup requires DJANGO_BACKUP_DIR.")

    keep_days = settings.DJANGO_BACKUP_KEEP_DAYS
    if keep_days is None or keep_days < 1:
        raise BackupError("DJANGO_BACKUP_KEEP_DAYS must be an integer of 1 or more.")

    return Path(backup_dir)


@contextmanager
def backup_lock(backup_dir):
    backup_dir.mkdir(parents=True, exist_ok=True)
    lock_path = backup_dir / ".backup.lock"
    with lock_path.open("a") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _write_dump(destination, *, force):
    if destination.exists() and not force:
        return False

    partial = destination.with_name(f".{destination.name}.partial")
    try:
        call_command(
            "dumpdata",
            *DUMP_LABELS,
            exclude=list(DUMP_EXCLUDES),
            natural_foreign=True,
            use_base_manager=True,
            indent=2,
            output=str(partial),
        )
        os.replace(partial, destination)
    except Exception:
        partial.unlink(missing_ok=True)
        raise

    return True


def _remove_old_files(backup_dir, today, keep_days):
    # keep_days includes today, so 14 keeps today and the 13 days before it.
    cutoff = today - timedelta(days=keep_days - 1)
    removed = []
    for path in backup_dir.iterdir():
        file_date = _backup_date(path)
        if file_date is None or file_date >= cutoff:
            continue
        path.unlink()
        removed.append(path)
    return tuple(removed)


def _backup_date(path: Path) -> date | None:
    match = BACKUP_FILE_NAME.match(path.name)
    if match is None:
        return None
    return date.fromisoformat(match.group(1))
