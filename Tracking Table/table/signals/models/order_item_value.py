from django.db.models.signals import pre_save
from django.dispatch import receiver
from table import models
from common.helpers import calculate_item_value


@receiver(pre_save, sender=models.Plate)
@receiver(pre_save, sender=models.Edge)
@receiver(pre_save, sender=models.Cutting)
@receiver(pre_save, sender=models.Edging)
@receiver(pre_save, sender=models.Other)
def update_item_value(sender, instance, **kwargs):
    instance.value = calculate_item_value(instance)
