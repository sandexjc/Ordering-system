from django.core.management.base import BaseCommand, CommandError

from common.backup.export_backup import BackupError
from common.backup.import_backup import import_backup


class Command(BaseCommand):
    help = (
        "Load one daily JSON backup from DJANGO_BACKUP_DIR. "
        "Matching primary keys are overwritten. "
        "Rows that exist only in the current database are left in place. "
        "Nothing is loaded unless --apply is passed. "
        "Requires DJANGO_FEATURES__DB_BACKUP=True."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "filename",
            help="Daily backup file name, backup-YYYY-MM-DD.json, inside DJANGO_BACKUP_DIR.",
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Load the file. Without this flag the command only describes the import.",
        )

    def handle(self, *args, **options):
        try:
            result = import_backup(
                options["filename"],
                apply=options["apply"],
                stdout=self.stdout,
            )
        except BackupError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            "Matching primary keys in the database will be overwritten. "
            "Rows that exist only in the current database will be left in place."
        )
        if result.applied:
            self.stdout.write(self.style.SUCCESS(f"Loaded {result.path.name}."))
        else:
            self.stdout.write(f"Not loaded. Pass --apply to load {result.path.name}.")
