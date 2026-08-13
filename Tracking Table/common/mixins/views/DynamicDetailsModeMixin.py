from django.urls import reverse


class DynamicDetailsModeMixin:

    """

    Hierarchy:
    DynamicDetailsModeMixin

    Shared expanded-row details behavior for table and vitrine:
    fetch.js appends ?dynamic=1 on the dynamic page; static boards do not.

    --- Fields inherited from parent classes ---

    No inherited class fields.

    """

    progress_update_url_name = None

    def is_dynamic_mode(self):
        return self.request.GET.get("dynamic") == "1"

    def add_dynamic_progress_context(self, context, pk):
        """Set dynamic_mode and, when dynamic, the click-to-toggle POST URL."""
        dynamic_mode = self.is_dynamic_mode()
        context["dynamic_mode"] = dynamic_mode
        if dynamic_mode and self.progress_update_url_name:
            context["progress_update_url"] = reverse(
                self.progress_update_url_name, kwargs={"pk": pk}
            )
        return dynamic_mode

    def post(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))
