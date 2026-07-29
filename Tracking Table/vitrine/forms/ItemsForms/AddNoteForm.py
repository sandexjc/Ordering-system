from common.forms import BaseModelForm
from common.mixins import FormFieldsSetupMixin
from vitrine.models import Note

class AddNoteForm(FormFieldsSetupMixin, BaseModelForm):

    """

    Hierarchy:
    FormFieldsStyleMixin -> BaseModelForm -> AddNoteForm
    forms.ModelForm -> BaseModelForm -> AddNoteForm
    FormFieldsSetupMixin -> AddNoteForm

    --- Fields inherited from BaseModelForm ---

    No explicit class fields inherited.

    --- Fields inherited from FormFieldsSetupMixin ---

    No explicit class fields inherited.

    """

    class Meta:
        model = Note
        fields = ("content",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_note_fields()