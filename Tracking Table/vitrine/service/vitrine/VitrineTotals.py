from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings

from common.service import BaseTotal
from vitrine.mapping import MODEL_RNAME_MAP


_RELATED_FIELDS = {
    "Frame": "frames_total",
    "Hole": "holes_total",
    "Other": "others_total",
    "Seal": "seals_total",
    "Glass": "glass_total",
    "Payment": "paid",
}


class VitrineTotals(BaseTotal):

    @staticmethod
    def _to_money(value):
        return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def manual_seal_total(cls, vitrine_instance):
        white_total = Decimal(vitrine_instance.white_seal_custom_amount) * Decimal(vitrine_instance.white_seal_price)
        black_total = Decimal(vitrine_instance.black_seal_custom_amount) * Decimal(vitrine_instance.black_seal_price)
        return cls._to_money(white_total + black_total)

    @classmethod
    def sync_seal_total(cls, vitrine_instance):
        manual_seal_enabled = settings.DJANGO_FEATURES__MANUAL_SEAL

        if manual_seal_enabled and vitrine_instance.vitrine_manual_seal:
            seals_total = cls.manual_seal_total(vitrine_instance)
        else:
            result = vitrine_instance.seals.for_order(vitrine_instance).aggregate(total=Sum("value"))
            seals_total = result["total"] if result["total"] is not None else Decimal("0.00")

        vitrine_instance.seals_total = seals_total
        vitrine_instance.save(update_fields=["seals_total"])

    @staticmethod
    def calculate_manufacturing(vitrine_instance):
        all_frames = vitrine_instance.frames.for_order(vitrine_instance)
        result = all_frames.aggregate(quantity=Sum('quantity'))
        quantity = result['quantity'] if result['quantity'] is not None else Decimal('0.00')
        price = getattr(vitrine_instance, "manufacturing_price")
        setattr(vitrine_instance, "manufacturing_total", (quantity * price))
        vitrine_instance.save(update_fields=["manufacturing_total"])

    @classmethod
    def update_total(cls, item):
        vitrine = item.vitrine_id
        item_model = item.__class__.__name__
        target_field = _RELATED_FIELDS.get(item_model)
        relation_name = MODEL_RNAME_MAP.get(item_model)

        # Update totals
        if item_model == "Seal":
            cls.sync_seal_total(vitrine)
        else:
            related_manager = getattr(vitrine, relation_name)
            cls.update_item_total(vitrine, related_manager, target_field)
        cls.calculate_manufacturing(vitrine)

        # Update order balance
        included_fields = [field for field in _RELATED_FIELDS.values()]
        included_fields.append("manufacturing_total")
        cls.update_order_balance(vitrine, included_fields)
