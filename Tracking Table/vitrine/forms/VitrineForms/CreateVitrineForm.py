from vitrine.models import Vitrine
from vitrine.forms import VitrineForm
from common.mixins import SetupFieldsMixin

class CreateVitrineForm(SetupFieldsMixin, VitrineForm):

    class Meta:
        model = Vitrine
        fields = ("owner", "telephone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customer contact information fields setup
        self.setup_contact_fields()