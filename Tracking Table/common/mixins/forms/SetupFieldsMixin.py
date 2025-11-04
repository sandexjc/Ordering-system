

class SetupFieldsMixin:

    """ Mixin that standardizes setup for fields in forms. """

    def setup_contact_fields(self):
        # Setup customer contact information fields
        if "owner" in self.fields:
            self.fields["owner"].widget.attrs["placeholder"] = "Име на клиент"
            self.fields["owner"].label = "Име на клиент"

        if "telephone" in self.fields:
            self.fields["telephone"].widget.attrs["placeholder"] = "Телефон"
            self.fields["telephone"].label = "Телефон"

    def setup_note_fields(self):
        # Setup note model fields
        if "content" in self.fields:
            self.fields["content"].widget.attrs.update({
                "cols": 5,
                "rows": 3,
                "placeholder": "Добави бележка ...",
            })
            self.fields["content"].label = "Бележка"
