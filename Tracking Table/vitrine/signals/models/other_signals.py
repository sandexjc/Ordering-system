from django.db.models.signals import pre_save
from django.dispatch import receiver
from vitrine.models import Other
from common.helpers import calculate_item_value


@receiver(pre_save, sender=Other)
def update_other_value(sender, other, **kwargs):
    other.value = calculate_item_value(other)