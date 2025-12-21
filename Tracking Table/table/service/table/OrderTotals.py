from common.service import BaseTotal
from table.mapping import MODEL_RNAME_MAP


_RELATED_FIELDS = {
    "Plate": "plates_total",
    "Edge": "edge_total",
    "Cutting": "cutting_total",
    "Edging": "edging_total",
    "Other": "others_total",
    "Payment": "paid",
}


class OrderTotals(BaseTotal):

    @classmethod
    def update_total(cls, item):
        order = item.order_id
        item_model = item.__class__.__name__
        target_field = _RELATED_FIELDS.get(item_model)
        relation_name = MODEL_RNAME_MAP.get(item_model)
        related_manager = getattr(order, relation_name)

        # Update totals
        cls.update_item_total(order, related_manager, target_field)

        # Update order balance
        included_fields = [field for field in _RELATED_FIELDS.values()]
        cls.update_order_balance(order, included_fields)
