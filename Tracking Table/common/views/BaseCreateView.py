from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.shortcuts import redirect

class BaseCreateView(LoginRequiredMixin, CreateView):

    """ A reusable base view for creating model objects. """

    template_name = "common/components/new_order.html"

    # Subclasses must define the below properties
    form_class = None
    change_model = None
    note_form_class = None
    related_field_name = None
    change_what = None
    redirect_name = None

    # --- pre save hook --- #
    def apply_creation_logic(self, object):

        """ Hook for subclasses to modify the object before it is saved. """

        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.note_form_class:
            context['add_note'] = self.note_form_class
        return context

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        note = self.request.POST.get('content', '').strip()
        user = self.request.user

        return self.form_valid(form, note, user)

    def form_valid(self, form, note, user):
        # Save main object
        self.object = form.save(commit=False)
        self.apply_creation_logic(self.object)
        self.object.save()

        # Create Change record
        if self.change_model and self.change_what:
            self.change_model.objects.create(
                **{
                    self.related_field_name: self.object,
                    "user": user.first_name,
                    "operation": "created",
                    "related_item": self.change_what,
                    "new_state": self.object.id,
                }
            )

        # Create Note (if form provided and note text is not empty)
        if self.note_form_class and note:
            note_form = self.note_form_class(self.request.POST)
            add_note = note_form.save(commit=False)
            setattr(add_note, self.related_field_name, self.object)
            add_note.user = user
            add_note.content = note
            add_note.save()

            # Create change record for Note
            if self.change_model:
                self.change_model.objects.create(
                    **{
                        self.related_field_name: self.object,
                        "user": user.first_name,
                        "operation": "created",
                        "related_item": "Note",
                        "new_state": note,
                    }
                )

        return redirect(self.redirect_name, self.object.pk)
