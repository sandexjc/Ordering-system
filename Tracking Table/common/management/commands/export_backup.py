from django.core.management.base import BaseCommand, CommandError

from common.backup import BackupError, export_backup


class Command(BaseCommand):
    help = (
        "Write today's database backup as JSON in DJANGO_BACKUP_DIR. "
        "Skips the file when it already exists unless --force is set. "
        "Removes daily files older than DJANGO_BACKUP_KEEP_DAYS. "
        "Requires DJANGO_FEATURES__DB_BACKUP=True."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Replace today's backup file if it already exists.",
        )

    def handle(self, *args, **options):
        try:
            result = export_backup(force=options["force"])
        except BackupError as exc:
            raise CommandError(str(exc)) from exc

        if result.written:
            self.stdout.write(self.style.SUCCESS(f"Wrote {result.path}."))
        else:
            self.stdout.write(f"Skipped {result.path}; today's backup already exists.")

        for path in result.removed:
            self.stdout.write(f"Removed {path.name}.")
