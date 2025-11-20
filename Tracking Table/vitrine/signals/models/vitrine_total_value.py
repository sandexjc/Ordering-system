from django.db.models.signals import post_save, post_delete
from common.signals import soft_deleted, restored
from django.dispatch import receiver
from vitrine import models
from common.helpers import calculate_order_totals


@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Frame)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Hole)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Other)
@receiver([post_save, post_delete, soft_deleted, restored], sender=models.Payment)
def update_vitrine_totals(sender, instance, **kwargs):
    
    # Each field corresponds to a related model whose items have a `value`
    related = {
        'frames_total': models.Frame,
        'holes_total': models.Hole,
        'others_total': models.Other,
        'seals_total': models.Seal,
        'paid': models.Payment,
    }

    calculate_order_totals(instance.vitrine_id, related)
