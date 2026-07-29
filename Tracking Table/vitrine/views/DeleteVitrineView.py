from common.views import BaseDeleteView
from vitrine.models import Vitrine


class DeleteVitrine(BaseDeleteView):

    """

    Hierarchy:
    LoginRequiredMixin -> SingleObjectMixin -> View -> BaseDeleteView -> DeleteVitrine

    --- Fields inherited from BaseDeleteView ---

    model = None

    """

    model = Vitrine
