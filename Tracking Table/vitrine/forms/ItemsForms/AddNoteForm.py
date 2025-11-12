from common.forms import BaseModelForm
from common.mixins import FormFieldsSetupMixin
from vitrine.models import Note

class AddNoteForm(FormFieldsSetupMixin, BaseModelForm):
    
    class Meta:
        model = Note
        fields = ("content",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_note_fields()