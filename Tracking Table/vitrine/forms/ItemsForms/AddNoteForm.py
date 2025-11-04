from common.forms import BaseModelForm
from common.mixins import SetupFieldsMixin
from vitrine.models import Note

class AddNoteForm(SetupFieldsMixin, BaseModelForm):
    
    class Meta:
        model = Note
        fields = ("content",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_note_fields()