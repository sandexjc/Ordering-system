from common.views import BaseUpdateView
from vitrine.models import Vitrine
from vitrine.forms import VitrineProgressForm

class UpdateVitrine(BaseUpdateView):

    """ Update vitrine app orders progress class. """

    model = Vitrine
    form_class = VitrineProgressForm
