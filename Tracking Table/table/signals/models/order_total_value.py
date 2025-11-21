from django.db.models.signals import post_save, post_delete
from common.signals import soft_deleted, restored
from django.dispatch import receiver
from table import models
from common.helpers import update_order_item_total, update_order_balance

_RELATED_FIELDS = {
    models.Plate: ["plates_total"],
    models.Edge: ["edge_total"],
    models.Cutting: ["cutting_total"],
    models.Edging: ["edging_total"],
    models.Other: ["others_total"],
    models.Payment: ["paid"],
}


@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Plate)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Edge)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Cutting)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Edging)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Other)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Payment)
def update_order_totals(sender, instance, **kwargs):

    # Calculate total_price for order related item
    update_order_item_total(instance.order_id, sender, _RELATED_FIELDS.get(sender))

    # Create list with all fields included in the Vitrine order balance and total_price
    # 1st loop: each list of fields
    # 2nd loop: each field inside that list
    included_fields = [field for field_list in _RELATED_FIELDS.values() for field in field_list]

    # Update Order total_price and balance
    update_order_balance(instance.order_id, included_fields)
