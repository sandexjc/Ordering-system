from vitrine.forms import VitrineForm
from vitrine.models import Vitrine
from common.mixins import FormFieldsSetupMixin

class EditVitrineForm(FormFieldsSetupMixin, VitrineForm):
    
    class Meta:
        model = Vitrine
        fields = ("id", "created_date", "owner", "telephone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customer contact information fields setup
        self.setup_contact_fields()