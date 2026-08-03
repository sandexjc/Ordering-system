from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from common.management.guards import require_debug_enabled
from table.models import (
    Change as TableChange,
    Cutting,
    Edge,
    Edging,
    Note as TableNote,
    Order,
    Other as TableOther,
    Payment as TablePayment,
    Plate,
)
from vitrine.models import (
    Change as VitrineChange,
    Frame,
    Glass,
    Hole,
    Note as VitrineNote,
    Other as VitrineOther,
    Payment as VitrinePayment,
    Seal,
    Vitrine,
)


# Item deletes can create Change rows via post_delete signals, so Change
# must be cleared after items and before the parent order model.
APP_DELETE_PLAN = {
    "table": {
        "order_model": Order,
        "fk_field": "order_id",
        "related_models": [
            Plate,
            Edge,
            Cutting,
            Edging,
            TableOther,
            TablePayment,
            TableNote,
            TableChange,
        ],
    },
    "vitrine": {
        "order_model": Vitrine,
        "fk_field": "vitrine_id",
        # Frame children first, then frames and other vitrine items.
        "related_models": [
            Hole,
            Glass,
            Seal,
            Frame,
            VitrineOther,
            VitrinePayment,
            VitrineNote,
            VitrineChange,
        ],
    },
}


class Command(BaseCommand):
    help = (
        "Permanently delete orders for a specified app "
        "(table or vitrine), including related items. "
        "Use --all or --count. Resets SQLite autoincrement when all "
        "orders are removed. Requires DJANGO_DEBUG=True."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            required=True,
            choices=sorted(APP_DELETE_PLAN.keys()),
            help="App whose orders should be deleted.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Delete all orders for the selected app.",
        )
        parser.add_argument(
            "--count",
            type=int,
            help="Delete this many newest orders (by ID descending).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many orders would be deleted without writing.",
        )

    def handle(self, *args, **options):
        require_debug_enabled("delete_orders")

        delete_all = options["all"]
        count = options["count"]

        if delete_all and count is not None:
            raise CommandError("Use either --all or --count, not both.")
        if not delete_all and count is None:
            raise CommandError("Provide --all or --count N.")
        if count is not None and count <= 0:
            raise CommandError("Count must be > 0.")

        app = options["app"]
        plan = APP_DELETE_PLAN[app]
        order_model = plan["order_model"]
        related_models = plan["related_models"]
        fk_field = plan["fk_field"]

        order_qs = order_model.objects.all_with_deleted()
        total_available = order_qs.count()

        if total_available == 0:
            self.stdout.write(self.style.WARNING(f"No {app} orders to delete."))
            return

        if delete_all:
            target_qs = order_qs
            target_count = total_available
            order_ids = None
        else:
            order_ids = list(
                order_qs.order_by("-id").values_list("pk", flat=True)[:count]
            )
            target_count = len(order_ids)
            target_qs = order_qs.filter(pk__in=order_ids)

        if target_count == 0:
            self.stdout.write(self.style.WARNING(f"No {app} orders to delete."))
            return

        scope = "all" if delete_all else f"{target_count} newest"
        if options["dry_run"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: would permanently delete {scope} {app} order(s) "
                    f"({target_count} of {total_available}) and related rows."
                )
            )
            return

        deleted_details = {}
        with transaction.atomic():
            for model in related_models:
                related_qs = model.objects.all_with_deleted()
                if order_ids is not None:
                    related_qs = related_qs.filter(**{f"{fk_field}__in": order_ids})
                deleted_count, details = related_qs.hard_delete()
                if deleted_count:
                    deleted_details.update(details)

            deleted_count, details = target_qs.hard_delete()
            deleted_details.update(details)

            remaining = order_model.objects.all_with_deleted().count()
            if remaining == 0:
                for model in related_models:
                    self._reset_sqlite_sequence(model)
                self._reset_sqlite_sequence(order_model)

        self.stdout.write(
            self.style.SUCCESS(
                f"Permanently deleted {scope} {app} order(s) "
                f"({target_count} of {total_available}). Details: {deleted_details}"
            )
        )

    def _reset_sqlite_sequence(self, model):
        if connection.vendor != "sqlite":
            return

        table_name = model._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM sqlite_sequence WHERE name = %s",
                [table_name],
            )
