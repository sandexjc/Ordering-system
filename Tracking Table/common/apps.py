from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"

    def ready(self):
        from common.db import connect_sqlite_pragmas, connect_sqlite_unicode_lower

        connect_sqlite_pragmas()
        connect_sqlite_unicode_lower()

        from common.backup.scheduler import start_backup_scheduler

        start_backup_scheduler()
