from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from table.models import Change
from table.forms import CreateOrderForm, AddNoteForm

from django.shortcuts import redirect

class CreateOrder(LoginRequiredMixin, CreateView):

    form_class = CreateOrderForm
    template_name = 'table/new_order.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['order_type'] = self.kwargs.get('type')  # comes from <str:type> in URL
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CreateOrder, self).get_context_data(**kwargs)
        context['add_note'] = AddNoteForm

        return context

    def post(self, request):

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        note = self.request.POST['content']
        user = self.request.user

        return self.form_valid(form, note, user)

    def form_valid(self, form, note, user):

        self.object = form.save(commit=False)
        self.object.save()

        Change.objects.create(order_id=self.object, user=user.first_name, operation='created', 
                                what='Order',new_state=self.object.id).save()

        add_note = AddNoteForm(self.request.POST).save(commit=False)
        add_note.order_id = self.object
        add_note.user = user
        add_note.content = note

        if note != '':
            add_note.save()

            Change.objects.create(order_id=self.object, user=user.first_name, operation='created', 
                                    what='Note', new_state=note).save()

        return redirect('table:editOrder', self.object.pk)