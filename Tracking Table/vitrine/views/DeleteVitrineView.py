from common.views import BaseDeleteView
from vitrine.models import Change, Vitrine


class DeleteVitrine(BaseDeleteView):

    """

    Hierarchy:
    LoginRequiredMixin -> SingleObjectMixin -> View -> BaseDeleteView -> DeleteVitrine

    --- Fields inherited from BaseDeleteView ---

    model = None
    http_method_names = ["post"]

    """

    model = Vitrine
    change_model = Change
    fk_field_name = "vitrine_id"
