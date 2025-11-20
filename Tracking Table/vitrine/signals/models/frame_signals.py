from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from vitrine.models import Frame, Hole, Glass, Seal
from common.signals import soft_deleted


@receiver(pre_save, sender=Frame)
def update_frame_value(sender, **kwargs):
    frame = kwargs["instance"]
    frame_length = ((frame.length * 2) + (frame.width * 2)) / Decimal("1000")
    value = (frame_length * frame.quantity) * frame.price
    frame.value = value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

@receiver(post_save, sender=Frame)
def create_or_update_items(sender, **kwargs):
    frame = kwargs["instance"]

    # Seal
    Seal.objects.update_or_create(
        vitrine_id = frame.vitrine_id,
        frame_id=frame,
        defaults={
            "seal_type": frame.profile_type if frame.profile_type == "Black" else "White",
            "quantity": ((frame.length * 2) + (frame.width * 2)) / 1000,
            "price": 1,
            }
    )

    # Holes
    Hole.objects.update_or_create(
        vitrine_id = frame.vitrine_id,
        frame_id=frame,
        defaults={
            "holes_position": frame.holes_position,
            "quantity": frame.holes_count,
            "price": 2,
        }
    )

    # GLASS
    Glass.objects.update_or_create(
        vitrine_id = frame.vitrine_id,
        frame_id=frame,
        defaults={
            "glass_type": frame.glass_type,
            "quantity": (frame.length * frame.width) / 1000000,
            "price": 0,
            }
    )

@receiver([soft_deleted, post_delete], sender=Frame)
def delete_frame_items(sender, **kwargs):
    frame = kwargs["instance"]
    Seal.frame_objects.for_frame(frame).update(deleted_at=timezone.now())
    Hole.frame_objects.for_frame(frame).update(deleted_at=timezone.now())
    Glass.frame_objects.for_frame(frame).update(deleted_at=timezone.now())
