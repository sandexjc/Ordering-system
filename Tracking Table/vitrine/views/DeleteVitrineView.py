from common.views import BaseDeleteView
from vitrine.models import Vitrine


class DeleteVitrine(BaseDeleteView):

    """ Delete view dedicated to Vitrine app. """

    model = Vitrine
