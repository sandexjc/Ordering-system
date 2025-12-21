from django.db.models import Sum
from decimal import Decimal

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
        related_manager = getattr(vitrine, relation_name)

        # Update totals
        cls.update_item_total(vitrine, related_manager, target_field)
        cls.calculate_manufacturing(vitrine)

        # Update order balance
        included_fields = [field for field in _RELATED_FIELDS.values()]
        included_fields.append("manufacturing_total")
        cls.update_order_balance(vitrine, included_fields)
