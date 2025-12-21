from django.db.models.signals import pre_save, post_save, post_delete
from common.signals import soft_deleted
from django.dispatch import receiver
from decimal import Decimal, ROUND_HALF_UP
from vitrine.models import Frame, Hole, Glass, Seal


_PROFILE_PRICE_MAP = {
    "Black": "black_profile_price",
    "Matte": "matte_profile_price",
    "Inox": "inox_profile_price",
}

_SEAL_PRICE_MAP = {
    "Black": "black_seal_price",
    "White": "white_seal_price",
}

@receiver(pre_save, sender=Frame)
def update_frame_value(sender, **kwargs):

    """ Calculate total frame value for current profile type. """

    frame = kwargs["instance"]
    vitrine = frame.vitrine_id
    
    frame.price = getattr(vitrine, _PROFILE_PRICE_MAP[frame.profile_type])
    frame_length = ((frame.length * 2) + (frame.width * 2)) / Decimal("1000")
    value = (frame_length * frame.quantity) * frame.price
    frame.value = value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


@receiver(post_save, sender=Frame)
def create_or_update_frame_items(sender, **kwargs):

    """ Create/Update frame related items. """

    frame = kwargs["instance"]
    vitrine = frame.vitrine_id

    seal_type = frame.profile_type if frame.profile_type == "Black" else "White"

    print("INSIDE FRAME post_save")
    print(f"SEAL TYPE: {seal_type}")
    print(f"SEAL QTY: {(((frame.length * 2) + (frame.width * 2)) / 1000) * frame.quantity}")
    print(f"SEAL PRICE: {getattr(vitrine, _SEAL_PRICE_MAP[seal_type])}\n")
    
    # Seal
    Seal.objects.update_or_create(
        vitrine_id = vitrine,
        frame_id=frame,
        defaults={
            "seal_type": seal_type,
            "quantity": (((frame.length * 2) + (frame.width * 2)) / 1000) * frame.quantity,
            "price": getattr(vitrine, _SEAL_PRICE_MAP[seal_type]),
            }
    )

    # Holes
    Hole.objects.update_or_create(
        vitrine_id = vitrine,
        frame_id=frame,
        defaults={
            "holes_position": frame.holes_position,
            "quantity": (frame.holes_count - 2 if frame.holes_count > 2 else 0) * frame.quantity,
            "price": getattr(vitrine, "add_hole_price"),
        }
    )

    # GLASS
    Glass.objects.update_or_create(
        vitrine_id = vitrine,
        frame_id=frame,
        defaults={
            "glass_type": frame.glass_type,
            "quantity": ((frame.length * frame.width) / 1000000) * frame.quantity,
            "price": 0,
            }
    )

@receiver([soft_deleted, post_delete], sender=Frame)
def delete_frame_items(sender, **kwargs):

    """ Handle frame items upon frame detele. """

    frame = kwargs["instance"]
    Seal.frame_objects.for_frame(frame).soft_delete()
    Hole.frame_objects.for_frame(frame).soft_delete()
    Glass.frame_objects.for_frame(frame).soft_delete()
