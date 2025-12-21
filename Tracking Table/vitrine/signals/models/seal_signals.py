from django.db.models.signals import pre_save
from django.dispatch import receiver
from common.helpers import calculate_item_value
from vitrine.models import Seal


@receiver(pre_save, sender=Seal)
def update_seal_value(sender, **kwargs):
    seal = kwargs["instance"]
    print("INSIDE SEAL pre_save")
    print(f"SEAL QTY: {seal.quantity}")
    print(f"SEAL PRICE: {seal.price}")
    seal.value = calculate_item_value(seal)
    print(f"SEAL VALUE: {seal.value}\n")