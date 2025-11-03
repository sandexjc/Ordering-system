

class ContactFieldsMixin:

    """ Mixin that standardizes setup for forms with 'owner' and 'telephone' fields. """

    def setup_contact_fields(self):
        if "owner" in self.fields:
            self.fields["owner"].widget.attrs["placeholder"] = "Име на клиент"
            self.fields["owner"].label = "Име на клиент"

        if "telephone" in self.fields:
            self.fields["telephone"].widget.attrs["placeholder"] = "Телефон"
            self.fields["telephone"].label = "Телефон"
