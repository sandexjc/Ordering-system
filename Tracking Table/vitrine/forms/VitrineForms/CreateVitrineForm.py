from vitrine.models import Vitrine
from vitrine.forms import VitrineForm
from common.mixins import FormFieldsSetupMixin

class CreateVitrineForm(FormFieldsSetupMixin, VitrineForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm -> VitrineForm -> CreateVitrineForm
    forms.ModelForm -> BaseModelForm -> VitrineForm -> CreateVitrineForm
    FormFieldsSetupMixin -> CreateVitrineForm

    --- Fields inherited from VitrineForm ---

    No explicit class fields inherited.

    --- Fields inherited from FormFieldsSetupMixin ---

    No explicit class fields inherited.

    """

    class Meta:
        model = Vitrine
        fields = ("owner", "telephone", "order_type")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customer contact information fields setup
        self.setup_contact_fields()
        self.fields["order_type"].label = "Поръчка/Оферта"