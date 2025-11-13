from vitrine.forms import VitrineForm, VitrineFormSet
from vitrine.models import Other, Vitrine
from django.forms import inlineformset_factory

class AddOtherForm(VitrineForm):

    class Meta:
        model = Other
        fields = ("description", "quantity", "price", "value")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_number("price")
        self.set_readonly("value")


# Formset for managing multiple Other items linked to a single Vitrine
OthersFormSet = inlineformset_factory(
    parent_model=Vitrine,
    model=Other,
    formset=VitrineFormSet,
    form=AddOtherForm,
    extra=3,
    can_delete_extra=False,
)