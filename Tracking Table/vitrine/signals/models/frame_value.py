from django.db.models.signals import pre_save
from django.dispatch import receiver
from decimal import Decimal, ROUND_HALF_UP
from vitrine.models import Frame

@receiver(pre_save, sender=Frame)
def update_frame_value(sender, instance, **kwargs):
    frame_length = ((instance.length * 2) + (instance.width * 2)) / 1000
    value = (frame_length * instance.quantity) * instance.price
    instance.value = value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)