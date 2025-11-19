from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from table import models
from common.helpers import calculate_order_totals


@receiver([post_save, post_delete], sender=models.Plate)
@receiver([post_save, post_delete], sender=models.Edge)
@receiver([post_save, post_delete], sender=models.Cutting)
@receiver([post_save, post_delete], sender=models.Edging)
@receiver([post_save, post_delete], sender=models.Other)
@receiver([post_save, post_delete], sender=models.Payment)
def update_order_totals(sender, instance, **kwargs):
    
    # Each field corresponds to a related model whose items have a `value`
    related = {
        'plates_total': models.Plate,
        'edge_total': models.Edge,
        'cutting_total': models.Cutting,
        'edging_total': models.Edging,
        'others_total': models.Other,
        'paid': models.Payment,
    }

    calculate_order_totals(instance.order_id, related)
