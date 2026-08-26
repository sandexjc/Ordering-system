from django.core.management.base import BaseCommand, CommandError

from table.models import Edge, Order, Plate
from table.service import OrderWeight


class Command(BaseCommand):
    help = (
        "Recalculate stored approximate weight for table orders from active "
        "plates and edges. Run after adding the Order.weight field migration. "
        "Does not require DJANGO_FEATURES__ORDER_WEIGHT."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print calculated weights without writing to the database.",
        )
        parser.add_argument(
            "--order-id",
            type=int,
            nargs="+",
            help="Recalculate only specific order IDs.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        queryset = Order.objects.all().order_by("pk")
        order_ids = options.get("order_id")
        if order_ids:
            queryset = queryset.filter(pk__in=order_ids)

        updated = unchanged = 0
        for order in queryset.iterator(chunk_size=200):
            previous = order.weight
            if dry_run:
                weight = OrderWeight.calculate_weight(
                    Plate.objects.for_order(order),
                    Edge.objects.for_order(order),
                )
            else:
                weight = OrderWeight.update_weight(order)

            if previous == weight:
                unchanged += 1
                continue
            if dry_run:
                self.stdout.write(
                    f"Order {order.pk}: {previous} -> {weight} кг"
                )
            updated += 1

        if order_ids and updated == 0 and unchanged == 0:
            raise CommandError("No matching table orders found.")

        action = "Would update" if dry_run else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} {updated} order(s); {unchanged} already current."
            )
        )
