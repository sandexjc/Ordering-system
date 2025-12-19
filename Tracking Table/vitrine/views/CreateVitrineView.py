from common.views import BaseCreateView
from vitrine.models import Change, Vitrine
from vitrine.forms import CreateVitrineForm, AddNoteForm
from vitrine.service import set_vitrine_prices


class CreateVitrine(BaseCreateView):

    model = Vitrine
    change_model = Change
    form_class = CreateVitrineForm
    note_form_class = AddNoteForm
    related_field_name = "vitrine_id"
    change_what = "Vitrine"
    redirect_name = "vitrine:edit_vitrine"

    def apply_creation_logic(self, object):
        # Set vitrine order prices
        set_vitrine_prices(object)