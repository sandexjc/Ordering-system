from dataclasses import dataclass
from pathlib import Path

from django.core.management import call_command
from django.core.serializers.base import ProgressBar

from common.backup.export_backup import BACKUP_FILE_NAME, BackupError, backup_directory, backup_lock


@dataclass(frozen=True)
class ImportResult:
    path: Path
    applied: bool


def import_backup(filename, *, apply=False, stdout=None):
    """
    Load one daily JSON backup from DJANGO_BACKUP_DIR.

    The filename must be backup-YYYY-MM-DD.json inside that directory.
    Nothing is loaded unless apply is set.
    """
    backup_dir = backup_directory()
    path = _backup_file(backup_dir, filename)

    if not apply:
        return ImportResult(path=path, applied=False)

    with backup_lock(backup_dir):
        _load(path, stdout)

    return ImportResult(path=path, applied=True)


def _backup_file(backup_dir, filename):
    name = Path(filename).name
    if name != filename or BACKUP_FILE_NAME.match(name) is None:
        raise BackupError(
            "Import only accepts a daily backup file named backup-YYYY-MM-DD.json "
            "from DJANGO_BACKUP_DIR."
        )

    path = backup_dir / name
    resolved = path.resolve()
    try:
        resolved.relative_to(backup_dir.resolve())
    except ValueError:
        raise BackupError("Import only accepts a file inside DJANGO_BACKUP_DIR.") from None

    if not resolved.is_file():
        raise BackupError(f"Backup file not found: {name}.")

    return resolved


def _load(path, stdout):
    total = _count_objects(path)
    stream = getattr(stdout, "_out", stdout)
    if total and stream is not None and getattr(stream, "isatty", lambda: False)():
        call_command(
            "loaddata",
            str(path),
            verbosity=3,
            stdout=_ImportProgress(stream, total),
        )
        return

    call_command("loaddata", str(path), stdout=stdout)


def _count_objects(path):
    count = 0
    with path.open() as handle:
        for line in handle:
            if line.lstrip().startswith('"model":'):
                count += 1
    return count


class _ImportProgress:
    """Turn loaddata's per-object lines into the same bar dumpdata uses."""

    def __init__(self, output, total):
        self.output = output
        self.bar = ProgressBar(output, total)

    def write(self, message=""):
        text = str(message)
        marker = "Processed "
        if marker in text and text.rstrip().endswith("object(s)."):
            number = text.split(marker, 1)[1].split(None, 1)[0]
            if number.isdigit():
                self.bar.update(min(int(number), self.bar.total_count))
                return
        self.output.write(text)

    def flush(self):
        self.output.flush()
