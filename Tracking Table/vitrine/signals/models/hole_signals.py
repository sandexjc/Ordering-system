from django.db.models.signals import pre_save
from django.dispatch import receiver
from vitrine.models import Hole


@receiver(pre_save, sender=Hole)
def update_hole_value(sender, **kwargs):

    """ Calculate hole total for related frame. """
    
    hole = kwargs["instance"]
    hole.value = hole.quantity * hole.price