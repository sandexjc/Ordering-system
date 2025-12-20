from common.views import BasePrintView
from common.service import CurrencyOperations
from vitrine.models import Vitrine
from vitrine.service import VitrineContextBuilder

class PrintVitrine(BasePrintView):

    model = Vitrine
    template_name = 'vitrine/print_vitrine.html'
    order_context = "vitrine"
    
    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(pk=pk, **kwargs)

        context.update(VitrineContextBuilder.build_context(context[self.order_context]))

        return context