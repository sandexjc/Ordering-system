from common.views import BaseUpdateView
from vitrine.models import Change, Vitrine
from vitrine.forms import VitrineProgressForm

class UpdateVitrine(BaseUpdateView):

    """

    Hierarchy:
    LoginRequiredMixin -> UpdateView -> BaseUpdateView -> UpdateVitrine

    --- Fields inherited from BaseUpdateView ---

    model = None
    form_class = None
    success_url = "/"

    """

    model = Vitrine
    form_class = VitrineProgressForm
    change_model = Change
    fk_field_name = "vitrine_id"
