from django.db.models.signals import pre_save
from django.dispatch import receiver
from common.helpers import calculate_item_value
from vitrine.models import Other


@receiver(pre_save, sender=Other)
def update_other_value(sender, **kwargs):
    other = kwargs["instance"]
    other.value = calculate_item_value(other)