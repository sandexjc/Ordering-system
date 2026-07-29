from vitrine.forms import VitrineForm
from vitrine.models import Vitrine

class VitrineProgressForm(VitrineForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm -> VitrineForm -> VitrineProgressForm
    forms.ModelForm -> BaseModelForm -> VitrineForm -> VitrineProgressForm

    --- Fields inherited from VitrineForm ---

    No explicit class fields inherited.

    """

    class Meta:
        model = Vitrine
        fields = ('order_taken', 'order_ready')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['order_taken', 'order_ready']:
            self.set_sm_checkbox(field_name)