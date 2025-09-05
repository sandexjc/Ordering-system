from common.forms import BaseModelForm
from table.models import Note

class AddNoteForm(BaseModelForm):
    
    class Meta:
        model = Note
        fields = ("content",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget.attrs.update({
            "cols": 5,
            "rows": 3,
            "placeholder": "Add note here ...",
        })
        self.fields["content"].label = "Notes"