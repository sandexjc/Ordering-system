from common.views import BaseCreateView
from vitrine.models import Change, Vitrine
from vitrine.forms import CreateVitrineForm, AddNoteForm


class CreateVitrine(BaseCreateView):

    model = Vitrine
    change_model = Change
    form_class = CreateVitrineForm
    note_form_class = AddNoteForm
    related_field_name = "vitrine_id"
    change_what = "Vitrine"
    redirect_name = "vitrine:edit_vitrine"