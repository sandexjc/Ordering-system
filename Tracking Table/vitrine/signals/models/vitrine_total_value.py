from django.db.models.signals import post_save, post_delete
from common.signals import soft_deleted, restored
from django.dispatch import receiver
from vitrine import models
from common.helpers import update_order_item_total, update_order_balance

_RELATED_FIELDS = {
    models.Frame: ["frames_total", "manufacturing_total"],
    models.Hole: ["holes_total"],
    models.Other: ["others_total"],
    models.Seal: ["seals_total"],
    models.Payment: ["paid"],
}


@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Frame)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Hole)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Seal)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Other)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Payment)
def update_vitrine_totals(sender, instance, **kwargs):

    # Calculate total_price for vitrine related item
    update_order_item_total(instance.vitrine_id, sender, _RELATED_FIELDS.get(sender))

    # Create list with all fields included in the Vitrine order balance and total_price
    # 1st loop: each list of fields
    # 2nd loop: each field inside that list
    included_fields = [field for field_list in _RELATED_FIELDS.values() for field in field_list]

    # Update total order_price balance
    update_order_balance(instance.vitrine_id, included_fields)
