from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from table import models
from common.mixins import BaseChangeSignalMixin


class TableChangeSignal(BaseChangeSignalMixin):
    change_model = models.Change
    fk_field_name = "order_id"


# Map model classes to their "related_item" names
MODEL_TO_RELATED_ITEM = {
    models.Plate: "Plate",
    models.Edge: "Edge",
    models.Cutting: "Cutting",
    models.Edging: "Edging",
    models.Other: "Other",
    models.Payment: "Payment",
}

# Map tracked fields from models
TRACKED_FIELDS = {
    "Plate": ["material", "manufacturer", "quantity", "price", "from_client"],
    "Edge": ["color_code", "length", "price"],
    "Cutting": ["cutting_type", "price"],
    "Edging": ["edging_type", "price"],
    "Other": ["description", "price"],
    "Payment": ["value", "payment_type"],
}

# --- DELETE HANDLERS ---- #
@receiver(post_delete, sender=models.Plate)
@receiver(post_delete, sender=models.Edge)
@receiver(post_delete, sender=models.Cutting)
@receiver(post_delete, sender=models.Edging)
@receiver(post_delete, sender=models.Other)
@receiver(post_delete, sender=models.Payment)
def log_item_deletion(sender, instance, **kwargs):

    TableChangeSignal.related_item = MODEL_TO_RELATED_ITEM.get(sender, sender.__name__)

    TableChangeSignal.set_log_change(
        related_instance=getattr(instance, "order_id", None),
        user=getattr(instance, "modified_by", None),
        operation="deleted",
        old_state=getattr(instance, "material", None)
        or getattr(instance, "color_code", None)
        or getattr(instance, "cutting_type", None)
        or getattr(instance, "edging_type", None)
        or str(instance) or "Delete",
    )


# --- CREATE HANDLERS --- #
@receiver(post_save, sender=models.Plate)
@receiver(post_save, sender=models.Edge)
@receiver(post_save, sender=models.Cutting)
@receiver(post_save, sender=models.Edging)
@receiver(post_save, sender=models.Other)
@receiver(post_save, sender=models.Payment)
def log_item_creation(sender, instance, created, **kwargs):
    # Only log new items
    if not created:
        return

    TableChangeSignal.related_item = MODEL_TO_RELATED_ITEM.get(sender, sender.__name__)

    TableChangeSignal.set_log_change(
        related_instance=getattr(instance, "order_id", None),
        user=getattr(instance, "modified_by", None)
        or getattr(instance, "created_by", None),
        operation="Created",
        new_state=getattr(instance, "material", None)
        or getattr(instance, "color_code", None)
        or getattr(instance, "cutting_type", None)
        or getattr(instance, "edging_type", None)
        or str(instance) or "Create",
    )


# --- PRE-SAVE: store old state before update --- #
@receiver(pre_save, sender=models.Plate)
@receiver(pre_save, sender=models.Edge)
@receiver(pre_save, sender=models.Cutting)
@receiver(pre_save, sender=models.Edging)
@receiver(pre_save, sender=models.Other)
@receiver(pre_save, sender=models.Payment)
def store_old_state(sender, instance, **kwargs):
    # new object — exit
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._old_state = {
            field: getattr(old_instance, field)
            for field in TRACKED_FIELDS.get(sender.__name__, [])
        }
    except sender.DoesNotExist:
        instance._old_state = {}


# --- UPDATE HANDLERS --- #
@receiver(post_save, sender=models.Plate)
@receiver(post_save, sender=models.Edge)
@receiver(post_save, sender=models.Cutting)
@receiver(post_save, sender=models.Edging)
@receiver(post_save, sender=models.Other)
@receiver(post_save, sender=models.Payment)
def log_item_update(sender, instance, created, **kwargs):

    """Compare old vs new values and log changes."""

    # Skip new items
    if created:
        return

    old_state = getattr(instance, "_old_state", None)
    if not old_state:
        return

    TableChangeSignal.related_item = sender.__name__
    user = getattr(instance, "modified_by", None) or getattr(instance, "created_by", None)

    for field, old_value in old_state.items():
        new_value = getattr(instance, field)
        if old_value != new_value:
            TableChangeSignal.set_log_change(
                related_instance=getattr(instance, "order_id", None),
                user=user,
                operation="Changed",
                old_state=f"{old_value}",
                new_state=f" → {new_value}",
            )
