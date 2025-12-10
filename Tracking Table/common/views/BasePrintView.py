from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class BasePrintView(LoginRequiredMixin, TemplateView):

    """ Base class for print views across multiple apps with shared logic. """

    # Subclasses must define the below properties
    model = None
    template_name = None
    