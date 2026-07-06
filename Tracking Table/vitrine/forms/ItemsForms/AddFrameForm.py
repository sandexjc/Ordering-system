from vitrine.forms import VitrineForm, VitrineFormSet
from vitrine.models import Frame, Vitrine
from django.forms import inlineformset_factory
from django.conf import settings

class AddFrameForm(VitrineForm):

    class Meta:
        model = Frame
        fields = (
            # frame related fields
            "profile_type", "length", "width", "quantity",
            # helper fields
            "holes_count", "holes_position", "glass_type", "auto_calculate_seal",
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_sm_dropdown("profile_type")
        self.set_sm_dropdown("holes_position")
        
        if settings.DJANGO_FEATURES__AUTO_SEAL_SELECT:
            self.set_switch("auto_calculate_seal")
        else:
            self.fields.pop("auto_calculate_seal", None)


# Formset for managing multiple Frames items linked to a single Vitrine
FrameFormSet = inlineformset_factory(
    parent_model=Vitrine,
    model=Frame,
    formset=VitrineFormSet,
    form=AddFrameForm,
    extra=5,
    can_delete_extra=False,
)