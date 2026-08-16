from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from common.mixins import DynamicFeatureFlagRequiredMixin
from common.service import CurrencyOperations


@method_decorator(csrf_protect, name="dispatch")
class BaseOrderFormModalView(DynamicFeatureFlagRequiredMixin, LoginRequiredMixin, View):

    """

    Hierarchy:
    DynamicFeatureFlagRequiredMixin -> BaseOrderFormModalView
    LoginRequiredMixin -> BaseOrderFormModalView
    View -> BaseOrderFormModalView

    Shared GET fragment + JSON POST for the dynamic create/edit order modal.
    Create and edit use one form UI; create saves the parent first, then formsets.

    Security:
    - login required
    - dynamic feature flag required
    - CSRF required (middleware + csrf_protect; client sends X-CSRFToken)

    --- Fields inherited from DynamicFeatureFlagRequiredMixin ---

    feature_setting_name = "DJANGO_FEATURES__DYNAMIC_CONTENT_LOADING"

    --- Fields inherited from LoginRequiredMixin ---

    No explicit class fields inherited.

    --- Fields inherited from View ---

    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]

    """

    http_method_names = ["get", "post"]

    # Subclasses must define
    model = None
    form_class = None
    note_form_class = None
    related_formsets = {}
    fk_field_name = None
    change_model = None
    change_what = None
    fragment_template_name = None
    rows_template_name = None
    rows_context_name = "orders"
    row_prefetch_related = ()
    create_url_name = None
    edit_url_name = None

    def get_order(self):
        pk = self.kwargs.get("pk")
        if pk is None:
            return None
        order = self.model.objects.get_by_id(pk)
        if order is None:
            raise Http404("Order not found.")
        return order

    def resolve_object(self):
        order = self.get_order()
        return order if order is not None else self.model()

    def get_formsets(self, instance, data=None):
        return {
            name: (
                formset_class(data, instance=instance)
                if data is not None
                else formset_class(instance=instance)
            )
            for name, formset_class in self.related_formsets.items()
        }

    def get_form_action_url(self):
        if self.object and self.object.pk:
            return reverse(self.edit_url_name, kwargs={"pk": self.object.pk})
        return reverse(self.create_url_name)

    def get_modal_title(self):
        if not self.object or not self.object.pk:
            return "Нова заявка"
        if getattr(self.object, "order_type", None) == "offer":
            return "Редактиране на оферта"
        return "Редактиране на поръчка"

    def get_currency_date(self):
        created_at = getattr(self.object, "created_at", None)
        if self.object and self.object.pk and created_at:
            return created_at.date()
        return timezone.now().date()

    def get_form_context(self, form, note_form, formsets):
        context = {
            "form": form,
            "add_note": note_form,
            "current_order": self.object,
            "currency": CurrencyOperations.get_currency(self.get_currency_date()),
            "form_action_url": self.get_form_action_url(),
            "modal_title": self.get_modal_title(),
            "is_create": not bool(self.object and self.object.pk),
        }
        context.update(formsets)
        return context

    def render_form_html(self, form, note_form, formsets):
        return render_to_string(
            self.fragment_template_name,
            self.get_form_context(form, note_form, formsets),
            request=self.request,
        )

    def fetch_order_for_rows(self, pk):
        queryset = self.model.objects.for_list(*self.row_prefetch_related)
        order = queryset.filter(pk=pk).first()
        if order is None:
            raise Http404("Order not found.")
        return order

    def render_rows_html(self, order):
        return render_to_string(
            self.rows_template_name,
            {self.rows_context_name: [order]},
            request=self.request,
        )

    def create_change_record(self, related_item, new_state):
        if not self.change_model or not self.fk_field_name:
            return
        self.change_model.objects.create(
            **{
                self.fk_field_name: self.object,
                "user": self.request.user.first_name,
                "operation": "created",
                "related_item": related_item,
                "new_state": new_state,
            }
        )

    def save_note(self, note_form):
        if not self.note_form_class:
            return
        note = note_form.save(commit=False)
        if not note.content:
            return
        setattr(note, self.fk_field_name, self.object)
        note.user = self.request.user.first_name
        note.run_workflow_save()
        return note

    def save_formsets(self, formsets):
        user = self.request.user.first_name
        for formset in formsets.values():
            formset.instance = self.object
            instances = formset.save(commit=False)
            for item in instances:
                item.modified_by = user
                setattr(item, self.fk_field_name, self.object)
                item.run_workflow_save()
            for item in formset.deleted_objects:
                item.modified_by = user
                item.run_workflow_delete()

    def success_payload(self):
        self.object = self.fetch_order_for_rows(self.object.pk)
        form = self.form_class(instance=self.object)
        note_form = self.note_form_class() if self.note_form_class else None
        formsets = self.get_formsets(instance=self.object)
        return {
            "status": "ok",
            "id": self.object.pk,
            "form_html": self.render_form_html(form, note_form, formsets),
            "rows_html": self.render_rows_html(self.object),
        }

    def error_payload(self, form, note_form, formsets, message, status=400):
        return JsonResponse(
            {
                "status": "error",
                "message": message,
                "form_html": self.render_form_html(form, note_form, formsets),
            },
            status=status,
        )

    def get(self, request, *args, **kwargs):
        self.object = self.resolve_object()
        form = self.form_class(instance=self.object if self.object.pk else None)
        note_form = self.note_form_class() if self.note_form_class else None
        formsets = self.get_formsets(instance=self.object)
        return HttpResponse(self.render_form_html(form, note_form, formsets))

    def post(self, request, *args, **kwargs):
        is_create = self.kwargs.get("pk") is None
        self.object = self.resolve_object()
        order_form = self.form_class(
            data=request.POST,
            instance=self.object if self.object.pk else None,
        )
        formsets = self.get_formsets(instance=self.object, data=request.POST)
        note_form = self.note_form_class(request.POST) if self.note_form_class else None

        note_valid = True if note_form is None else note_form.is_valid()
        all_valid = (
            order_form.is_valid()
            and note_valid
            and all(formset.is_valid() for formset in formsets.values())
        )

        if not all_valid:
            return self.error_payload(
                order_form,
                note_form,
                formsets,
                "Възникна грешка!",
            )

        try:
            with transaction.atomic():
                self.object = order_form.save(commit=False)
                self.object.run_workflow_save()

                if is_create:
                    self.create_change_record(self.change_what, self.object.id)

                if note_form is not None:
                    note = self.save_note(note_form)
                    if is_create and note is not None:
                        self.create_change_record("Note", note.content)

                self.save_formsets(formsets)
        except Exception as exc:
            return JsonResponse(
                {"status": "error", "message": str(exc)},
                status=500,
            )

        return JsonResponse(self.success_payload())
