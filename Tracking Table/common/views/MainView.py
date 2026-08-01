from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import time


class MainView(LoginRequiredMixin, TemplateView):

    """

    Hierarchy:
    LoginRequiredMixin -> MainView
    TemplateView -> MainView

    --- Fields inherited from LoginRequiredMixin ---

    No explicit class fields inherited.

    --- Fields inherited from TemplateView ---

    No explicit class fields inherited.

    """

    def get_time_of_day(self):
        # Returns a friendly time label
        current_time = time.localtime(time.time())
        if current_time.tm_hour in range(7, 10):
            return 'Morning'
        elif current_time.tm_hour in range(11, 15):
            return 'Day'
        elif current_time.tm_hour in range(16, 19):
            return 'Afternoon'
        else:
            return 'Night'
