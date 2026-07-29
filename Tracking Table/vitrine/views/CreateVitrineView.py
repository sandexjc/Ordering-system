from common.views import BaseCreateView
from vitrine.models import Change, Vitrine
from vitrine.forms import CreateVitrineForm, AddNoteForm


class CreateVitrine(BaseCreateView):

    """

    Hierarchy:
    LoginRequiredMixin -> CreateView -> BaseCreateView -> CreateVitrine

    --- Fields inherited from BaseCreateView ---

    template_name = "common/components/new_order.html"
    form_class = None
    change_model = None
    note_form_class = None
    related_field_name = None
    change_what = None
    redirect_name = None

    """

    model = Vitrine
    change_model = Change
    form_class = CreateVitrineForm
    note_form_class = AddNoteForm
    related_field_name = "vitrine_id"
    change_what = "Vitrine"
    redirect_name = "vitrine:edit_vitrine"
