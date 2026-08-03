from datetime import timedelta
from decimal import Decimal
from random import choice, randint, uniform

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from common.management.guards import require_debug_enabled
from table.models import Edge, Order, Payment, Plate
from vitrine.models import Frame, Hole, Vitrine


MATERIALS = [
    "W980 ST2",
    "H1180 ST37",
    "U702 ST9",
    "H3734 ST9",
    "W1000 ST",
]
EDGE_TYPES = [
    "ABS 22x0.8",
    "ABS 23x1",
    "ABS 42x2",
    "PVC 22x0.4",
]
GLASS_TYPES = [
    "Float 4mm",
    "Triplex 3.3.1",
    "Satinato",
    "Stopsol",
]


def money(value: float) -> Decimal:
    return Decimal(str(round(value, 2)))


def ascending_created_dates(count):
    """Build strictly increasing created_date values for sequential order IDs."""
    if count <= 0:
        return []

    now = timezone.now()
    start = now - timedelta(days=365)
    span_seconds = max(int((now - start).total_seconds()), count)

    dates = []
    for index in range(count):
        # Evenly spaced timeline with a small random jitter that never
        # reaches the next slot, so order remains strictly ascending.
        slot = start + timedelta(seconds=(span_seconds * index) // count)
        max_jitter = max(span_seconds // count - 1, 0)
        jitter = randint(0, max_jitter) if max_jitter else 0
        dates.append(slot + timedelta(seconds=jitter))
    return dates


class Command(BaseCommand):
    help = (
        "Seed demo orders for a specified app: "
        "table (plates, edges, payments) or vitrine (frames, holes). "
        "Requires DJANGO_DEBUG=True."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            required=True,
            choices=("table", "vitrine"),
            help="App whose orders should be seeded.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of orders to create (default: 100).",
        )
        parser.add_argument(
            "--locale",
            type=str,
            default="bg_BG",
            help="Faker locale (default: bg_BG).",
        )

    def handle(self, *args, **options):
        require_debug_enabled("seed_orders")

        try:
            from faker import Faker
        except ImportError as exc:
            raise CommandError(
                "Faker is required. Install it with: pip install faker"
            ) from exc

        fake = Faker(options["locale"])
        app = options["app"]
        count = options["count"]

        if count < 0:
            raise CommandError("Count must be >= 0.")

        with transaction.atomic():
            if app == "table":
                stats = self._seed_table_orders(fake, count)
                message = (
                    f"Created {stats['orders']} table orders "
                    f"({stats['plates']} plates, "
                    f"{stats['edges']} edges, "
                    f"{stats['payments']} payments)."
                )
            else:
                stats = self._seed_vitrine_orders(fake, count)
                message = (
                    f"Created {stats['orders']} vitrine orders "
                    f"({stats['frames']} frames, "
                    f"{stats['holes']} holes)."
                )

        self.stdout.write(self.style.SUCCESS(message))

    def _seed_table_orders(self, fake, count):
        plates_created = edges_created = payments_created = 0
        created_dates = ascending_created_dates(count)

        for created_date in created_dates:
            order = Order.objects.create(
                owner=fake.name()[:50],
                telephone=fake.phone_number()[:14],
                order_type=choice(["order", "offer"]),
                order_ready=choice([True, False]),
                order_taken=False,
                invoice=choice([True, False]),
                created_date=created_date,
            )

            plates_total = Decimal("0.00")
            edge_total = Decimal("0.00")

            for _ in range(randint(1, 4)):
                quantity = money(uniform(0.5, 8.0))
                price = money(uniform(20, 180))
                value = money(float(quantity) * float(price))
                Plate.objects.create(
                    order_id=order,
                    manufacturer=choice(["Egger", "Kronospan", "Other"]),
                    material=choice(MATERIALS),
                    quantity=quantity,
                    price=price,
                    value=value,
                    from_client=choice([True, False]),
                    ordered=choice([True, False]),
                    delivered=choice([True, False]),
                    cutted=choice([True, False]),
                    edged=choice([True, False]),
                )
                plates_total += value
                plates_created += 1

            for _ in range(randint(1, 3)):
                quantity = money(uniform(0.5, 50.0))
                price = money(uniform(1, 12))
                value = money(float(quantity) * float(price))
                Edge.objects.create(
                    order_id=order,
                    edge_type=choice(EDGE_TYPES),
                    color_code=fake.bothify(text="??##").upper(),
                    quantity=quantity,
                    price=price,
                    value=value,
                    ordered=choice([True, False]),
                    delivered=choice([True, False]),
                    visible=True,
                )
                edge_total += value
                edges_created += 1

            total_price = plates_total + edge_total
            paid = Decimal("0.00")
            payment_count = randint(0, 2)
            remaining = float(total_price)

            for i in range(payment_count):
                if remaining <= 0:
                    break
                if i == payment_count - 1 and choice([True, False]):
                    amount = money(remaining)
                else:
                    amount = money(min(remaining, uniform(20, max(remaining, 20))))
                Payment.objects.create(
                    order_id=order,
                    value=amount,
                    payment_method=choice(["Cash", "Card", "Bank"]),
                )
                paid += amount
                remaining -= float(amount)
                payments_created += 1

            order.plates_total = plates_total
            order.edge_total = edge_total
            order.cutting_total = Decimal("0.00")
            order.edging_total = Decimal("0.00")
            order.others_total = Decimal("0.00")
            order.total_price = total_price
            order.paid = paid
            order.balance = total_price - paid
            order.save(
                update_fields=[
                    "plates_total",
                    "edge_total",
                    "cutting_total",
                    "edging_total",
                    "others_total",
                    "total_price",
                    "paid",
                    "balance",
                ]
            )

        return {
            "orders": count,
            "plates": plates_created,
            "edges": edges_created,
            "payments": payments_created,
        }

    def _seed_vitrine_orders(self, fake, count):
        frames_created = holes_created = 0
        created_dates = ascending_created_dates(count)

        for created_date in created_dates:
            add_hole_price = money(uniform(5, 25))
            black_price = money(uniform(15, 40))
            matte_price = money(uniform(18, 45))
            inox_price = money(uniform(25, 60))

            vitrine = Vitrine.objects.create(
                owner=fake.name()[:50],
                telephone=fake.phone_number()[:14],
                order_type=choice(["order", "offer"]),
                order_ready=choice([True, False]),
                order_taken=False,
                black_profile_price=black_price,
                matte_profile_price=matte_price,
                inox_profile_price=inox_price,
                white_seal_price=money(uniform(2, 8)),
                black_seal_price=money(uniform(2, 8)),
                add_hole_price=add_hole_price,
                manufacturing_price=money(uniform(10, 50)),
                created_date=created_date,
            )

            frames_total = Decimal("0.00")
            holes_total = Decimal("0.00")
            profile_price_map = {
                "Black": black_price,
                "Matte": matte_price,
                "Inox": inox_price,
            }

            for _ in range(randint(1, 3)):
                profile_type = choice(["Black", "Matte", "Inox"])
                length = randint(400, 2500)
                width = randint(300, 1800)
                quantity = randint(1, 4)
                price = profile_price_map[profile_type]
                value = money(float(price) * quantity)
                holes_position = choice(["length", "width"])
                holes_count = randint(0, 4)

                frame = Frame.objects.create(
                    vitrine_id=vitrine,
                    profile_type=profile_type,
                    length=length,
                    width=width,
                    quantity=quantity,
                    price=price,
                    value=value,
                    holes_count=holes_count,
                    holes_position=holes_position,
                    glass_type=choice(GLASS_TYPES),
                    auto_calculate_seal=True,
                )
                frames_total += value
                frames_created += 1

                if holes_count > 0:
                    hole_value = money(float(add_hole_price) * holes_count)
                    Hole.objects.create(
                        vitrine_id=vitrine,
                        frame_id=frame,
                        holes_position=holes_position,
                        quantity=holes_count,
                        price=add_hole_price,
                        value=hole_value,
                    )
                    holes_total += hole_value
                    holes_created += 1

            total_price = frames_total + holes_total
            paid = money(float(total_price) * uniform(0, 1)) if total_price else Decimal("0.00")

            vitrine.frames_total = frames_total
            vitrine.holes_total = holes_total
            vitrine.others_total = Decimal("0.00")
            vitrine.seals_total = Decimal("0.00")
            vitrine.glass_total = Decimal("0.00")
            vitrine.manufacturing_total = Decimal("0.00")
            vitrine.total_price = total_price
            vitrine.paid = paid
            vitrine.balance = total_price - paid
            vitrine.save(
                update_fields=[
                    "frames_total",
                    "holes_total",
                    "others_total",
                    "seals_total",
                    "glass_total",
                    "manufacturing_total",
                    "total_price",
                    "paid",
                    "balance",
                ]
            )

        return {
            "orders": count,
            "frames": frames_created,
            "holes": holes_created,
        }
