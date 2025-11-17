from vitrine.forms import VitrineForm, VitrineFormSet
from vitrine.models import Frame, Vitrine, Hole, Glass, Seal
from django.forms import inlineformset_factory, IntegerField, ChoiceField, CharField

class AddFrameForm(VitrineForm):

    # Non model fields
    holes_positions = [
        ('length', 'дължина'),
        ('width', 'широчина'),
    ]

    holes_count = IntegerField(required=False, min_value=0)
    holes_position = ChoiceField(required=False, choices=holes_positions, initial="length")
    glass_type = CharField(required=False, initial="")

    # Model fields
    class Meta:
        model = Frame
        fields = ("profile_type", "length", "width", "quantity", "price")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_sm_dropdown("profile_type")
        self.set_sm_dropdown("holes_position")

        # Populate non-model fields if Frame exists
        if self.instance and self.instance.pk:
            # HOLES
            hole = Hole.frame_objects.for_frame(self.instance).first()
            if hole:
                self.fields['holes_count'].initial = hole.quantity
                self.fields['holes_position'].initial = hole.holes_position

            # GLASS
            glass = Glass.frame_objects.for_frame(self.instance).first()
            if glass:
                self.fields['glass_type'].initial = glass.glass_type


# Formset for managing multiple Frames items linked to a single Vitrine
FrameFormSet = inlineformset_factory(
    parent_model=Vitrine,
    model=Frame,
    formset=VitrineFormSet,
    form=AddFrameForm,
    extra=5,
    can_delete_extra=False,
)