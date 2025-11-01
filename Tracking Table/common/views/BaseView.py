# views/base.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from main.forms import SearchForm, FilterForm
import time

class BaseView(LoginRequiredMixin, TemplateView):

    """ Base view logic for all apps sharing main site page """

    # Forms remain the same for all apps
    search_form_class = SearchForm
    filter_form_class = FilterForm

    # Subclasses must define the below properties
    model = None
    template_name = None
    clients_type = None
    navigation = None

    # Default count of items to display
    default_items_count = 100

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['filter_badge'] = True
        context['nav_select'] = self.navigation

        if self.request.method == "POST":
            action = self.request.POST.get('action')

            if action == 'Search':
                context.update(self.handle_search())
            elif action == 'Filter':
                context.update(self.handle_filter())

        else:
            context['orders'] = self.get_default_queryset()
            context['search_form'] = self.search_form_class
            context['filter_form'] = self.filter_form_class
            context['badges'] = False

        context['visible_items'] = len(context['orders'])
        context['current_time'] = self.get_time_of_day()
        return context

    def handle_search(self):
        # Handles search logic and delegates query generation to subclasses
        data = self.request.POST
        search_category = data.get('category')
        search_value = data.get('search_field')

        context = {
            'filter_form': self.filter_form_class,
            'search_form': self.search_form_class(self.request.POST),
            'category': search_category,
            'search_string': search_value,
            'search_error': False,
        }

        if not search_value:
            context['badges'] = False
            context['orders'] = []
            return context

        try:
            context['orders'] = self.get_queryset_by_search(search_category, search_value)
        except Exception:
            context['search_error'] = True
            context['orders'] = []

        context['badges'] = True
        return context

    def handle_filter(self):
        # Handles filtering logic
        data = self.request.POST
        fast_select = data.get('fast_select')

        if fast_select and fast_select.isnumeric():
            orders = self.get_queryset_latest_by_count(int(fast_select))
            filter_badge = True
        else:
            orders = self.get_queryset_all()
            filter_badge = False

        return {
            'orders': orders,
            'filter_badge': filter_badge,
            'search_form': self.search_form_class,
            'filter_form': self.filter_form_class(self.request.POST),
        }

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

    # These methods should be implemented by subclasses:
    def get_queryset_by_search(self, category, search_value):
        raise NotImplementedError

    def get_queryset_latest_by_count(self, count):
        raise NotImplementedError

    def get_queryset_all(self):
        raise NotImplementedError

    def get_default_queryset(self):
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())
