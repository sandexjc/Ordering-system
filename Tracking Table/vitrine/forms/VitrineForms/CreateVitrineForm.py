from vitrine.models import Vitrine
from vitrine.forms import VitrineForm
from common.mixins import ContactFieldsMixin

class CreateVitrineForm(ContactFieldsMixin, VitrineForm):

    class Meta:
        model = Vitrine
        fields = ("owner", "telephone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Shared client contact fields
        self.setup_contact_fields()