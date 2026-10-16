class OrderHistoryMixin:

    """

    Hierarchy:
    OrderHistoryMixin

    Writes one Change row per user action on an order or vitrine.
    Views set change_model and fk_field_name. Totals, weight, and prices are not logged.

    """

    change_model = None
    fk_field_name = None

    _ITEM_LABELS = {
        "Order": "Поръчка",
        "Vitrine": "Витрина",
        "Note": "Бележка",
        "Plate": "Плоча",
        "Edge": "Кант",
        "Cutting": "Рязане",
        "Edging": "Кантиране",
        "Other": "Друго",
        "Payment": "Плащане",
        "Frame": "Рамка",
    }

    _FIELD_LABELS = {
        "owner": "клиент",
        "telephone": "телефон",
        "order_type": "тип",
        "created_date": "дата",
        "vitrine_manual_seal": "ръчно уплътнение",
        "white_seal_custom_amount": "бяло уплътнение",
        "black_seal_custom_amount": "черно уплътнение",
        "material": "материал",
        "manufacturer": "производител",
        "from_client": "от клиент",
        "quantity": "количество",
        "price": "цена",
        "description": "описание",
        "edge_type": "вид кант",
        "color_code": "цвят",
        "visible": "видим",
        "cutting_type": "вид рязане",
        "edging_type": "вид кантиране",
        "payment_method": "начин на плащане",
        "value": "сума",
        "profile_type": "профил",
        "length": "дължина",
        "width": "широчина",
        "holes_count": "отвори",
        "holes_position": "позиция на отворите",
        "glass_type": "стъкло",
        "auto_calculate_seal": "автоматично уплътнение",
        "ordered": "поръчана",
        "delivered": "доставена",
        "cutted": "рязане",
        "edged": "кантиране",
        "order_taken": "взета",
        "invoice": "фактура",
        "order_ready": "готова",
    }

    _SKIP_FIELDS = {
        "id",
        "created_date",
        "white_seal_type",
        "black_seal_type",
        "white_seal_total_value",
        "black_seal_total_value",
    }

    def write_history(self, parent, operation, related_item, field_label="", old_state=None, new_state=None):
        if not self.change_model or not self.fk_field_name or parent is None:
            return
        actor = self.request.user
        self.change_model.objects.create(
            **{
                self.fk_field_name: parent,
                "user": self._actor_name(actor),
                "actor": actor if getattr(actor, "pk", None) else None,
                "operation": operation,
                "related_item": related_item,
                "field_label": field_label or "",
                "current_state": "" if old_state is None else str(old_state),
                "new_state": "" if new_state is None else str(new_state),
            }
        )

    def log_created(self, parent, model_name):
        self.write_history(
            parent,
            "създаде",
            self._ITEM_LABELS.get(model_name, model_name),
            new_state=parent.pk,
        )

    def log_deleted(self, parent):
        self.write_history(
            parent,
            "изтри",
            self._ITEM_LABELS.get(parent.__class__.__name__, parent.__class__.__name__),
            new_state=parent.pk,
        )

    def log_note(self, parent, content):
        self.write_history(parent, "добави", self._ITEM_LABELS["Note"], new_state=content)

    _PROGRESS_STEPS = ("ordered", "delivered", "cutted", "edged")

    def log_progress_changes(self, parent, item, before):
        steps = [name for name in self._PROGRESS_STEPS if name in before]
        if steps and len(steps) == len(before):
            self._log_progress_status(parent, item, before, steps)
            return
        for field_name, old_value in before.items():
            new_value = getattr(item, field_name)
            if old_value == new_value:
                continue
            label = self._FIELD_LABELS.get(field_name, field_name)
            self.write_history(
                parent,
                "промени",
                self._item_label(item),
                label,
                f"{label} {self._display(old_value)}",
                self._display(new_value),
            )

    def _log_progress_status(self, parent, item, before, steps):
        after = {name: getattr(item, name) for name in steps}
        old_step = self._reached_step(before, steps)
        new_step = self._reached_step(after, steps)
        if old_step == new_step:
            return
        self.write_history(
            parent,
            "промени",
            self._item_label(item),
            "статус",
            self._FIELD_LABELS.get(old_step, "няма"),
            self._FIELD_LABELS.get(new_step, "няма"),
        )

    def _reached_step(self, values, steps):
        reached = None
        for name in steps:
            if values.get(name):
                reached = name
            else:
                break
        return reached

    def log_order_form(self, parent, form):
        for field_name, old_value, new_value in self._field_changes(form):
            saved = getattr(parent, field_name, new_value)
            if saved == old_value:
                continue
            self.write_history(
                parent,
                "промени",
                self._ITEM_LABELS.get(parent.__class__.__name__, parent.__class__.__name__),
                self._FIELD_LABELS.get(field_name, field_name),
                self._display(old_value, form, field_name),
                self._display(saved, form, field_name),
            )

    def log_formset(self, parent, formset, saved_instances):
        saved_ids = {id(instance) for instance in saved_instances}
        for form in formset.forms:
            if id(getattr(form, "instance", None)) not in saved_ids:
                continue
            if form.instance.pk and self._was_new(form):
                self.write_history(
                    parent,
                    "добави",
                    self._ITEM_LABELS.get(form.instance.__class__.__name__, form.instance.__class__.__name__),
                    new_state=self._summary(form.instance),
                )
                continue
            for field_name, old_value, new_value in self._field_changes(form):
                self.write_history(
                    parent,
                    "промени",
                    self._item_label(form.instance),
                    self._FIELD_LABELS.get(field_name, field_name),
                    self._display(old_value, form, field_name),
                    self._display(new_value, form, field_name),
                )

    def log_deleted_item(self, parent, item):
        self.write_history(parent, "изтри", self._item_label(item))

    def mark_new_forms(self, formset):
        for form in formset.forms:
            form._history_was_new = not bool(getattr(form.instance, "pk", None))

    def _was_new(self, form):
        return bool(getattr(form, "_history_was_new", False))

    def _field_changes(self, form):
        if not getattr(form, "changed_data", None):
            return
        model_name = form.instance.__class__.__name__
        for field_name in form.changed_data:
            if self._skip_field(field_name, form, model_name):
                continue
            old_value = form.initial.get(field_name)
            new_value = form.cleaned_data.get(field_name)
            if old_value == new_value:
                continue
            yield field_name, old_value, new_value

    def _skip_field(self, field_name, form, model_name):
        if field_name in self._SKIP_FIELDS or field_name not in form.fields:
            return True
        if field_name == "value" and model_name != "Payment":
            return True
        return False

    def _item_label(self, item):
        base = self._ITEM_LABELS.get(item.__class__.__name__, item.__class__.__name__)
        detail = self._summary(item)
        if not detail:
            return base
        return f"{base} {detail}"

    def _summary(self, source):
        model_name = source.__class__.__name__
        if model_name == "Plate":
            return self._read(source, "material")
        if model_name == "Edge":
            return self._read(source, "color_code") or self._read(source, "edge_type")
        if model_name == "Cutting":
            return self._read(source, "cutting_type")
        if model_name == "Edging":
            return self._read(source, "edging_type")
        if model_name == "Other":
            return self._read(source, "description")
        if model_name == "Payment":
            method = self._read(source, "payment_method")
            amount = self._read(source, "value")
            return " ".join(part for part in (self._display(method), self._display(amount)) if part)
        if model_name == "Frame":
            return f"{self._read(source, 'length')}x{self._read(source, 'width')}"
        return ""

    def _read(self, source, name):
        if isinstance(source, dict):
            return source.get(name)
        return getattr(source, name, None)

    def _display(self, value, form=None, field_name=None):
        if isinstance(value, bool):
            return "да" if value else "не"
        if form is not None and field_name in getattr(form, "fields", {}):
            choices = getattr(form.fields[field_name], "choices", None)
            if choices:
                labels = {key: label for key, label in choices}
                if value in labels:
                    return str(labels[value])
        if value is None:
            return ""
        return str(value)

    def _actor_name(self, actor):
        first_name = getattr(actor, "first_name", None)
        if first_name is None:
            return str(actor) if actor else "System"
        return first_name or getattr(actor, "username", None) or "System"
