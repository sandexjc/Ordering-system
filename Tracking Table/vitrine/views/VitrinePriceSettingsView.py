from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from accounts.mixins import AdminRequiredMixin
from vitrine.forms import VitrinePriceConfigForm
from vitrine.models import VitrinePriceConfig


class VitrinePriceSettings(AdminRequiredMixin, UpdateView):
    model = VitrinePriceConfig
    form_class = VitrinePriceConfigForm
    template_name = "vitrine/price-settings.html"
    success_url = reverse_lazy("vitrine:price-settings")

    def get_object(self, queryset=None):
        return VitrinePriceConfig.objects.get_current()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["price_form"] = context["form"]
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            form.save()
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "ok": True,
                        "message": "Цените за витрини са запазени успешно.",
                    }
                )
            return super().form_valid(form)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            message = "Възникна грешка при запазване."
            if form.non_field_errors():
                message = str(form.non_field_errors()[0])
            else:
                for field_errors in form.errors.values():
                    if field_errors:
                        message = str(field_errors[0])
                        break
            return JsonResponse(
                {
                    "ok": False,
                    "message": message,
                    "errors": form.errors,
                },
                status=400,
            )

        return self.form_invalid(form)
