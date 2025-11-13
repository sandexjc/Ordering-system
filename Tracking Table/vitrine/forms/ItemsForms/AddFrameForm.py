from vitrine.forms import VitrineForm, VitrineFormSet
from vitrine.models import Frame, Vitrine
from django.forms import inlineformset_factory, IntegerField, ChoiceField, CharField

class AddFrameForm(VitrineForm):

    # Non model fields
    holes_positions = [
        ('length', 'дължина'),
        ('width', 'широчина'),
    ]

    holes_count = IntegerField(required=False, min_value=0)
    holes_position = ChoiceField(required=False, choices=holes_positions, default="length")
    glass_type = CharField(required=False)

    # Model fields
    class Meta:
        model = Frame
        fields = ("profile_type", "length", "width", "quantity", "price")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_sm_dropdown("profile_type")
        self.set_number("length")
        self.set_number("width")
        self.set_readonly("quantity")
        self.set_number("price")
        self.set_sm_dropdown("holes_position")


# Formset for managing multiple Frames items linked to a single Vitrine
FrameFormSet = inlineformset_factory(
    parent_model=Vitrine,
    model=Frame,
    formset=VitrineFormSet,
    form=AddFrameForm,
    extra=3,
    can_delete_extra=False,
)