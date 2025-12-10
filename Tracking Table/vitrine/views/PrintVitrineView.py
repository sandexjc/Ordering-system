from common.views import BasePrintView
from vitrine.models import Vitrine
from vitrine.service import VitrineContextBuilder

class PrintVitrine(BasePrintView):

    model = Vitrine
    template_name = 'vitrine/print_vitrine.html'
    
    def get_context_data(self, pk, **kwargs):
        context = super(PrintVitrine, self).get_context_data(**kwargs)
        vitrine = Vitrine.objects.get_by_id(pk)
        
        context['vitrine'] = vitrine
        context.update(VitrineContextBuilder.build(vitrine))

        return context