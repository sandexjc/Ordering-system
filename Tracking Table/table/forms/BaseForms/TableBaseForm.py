from common.forms import BaseModelForm

class TableForm(BaseModelForm):
    
    # Intermediate level base model form for all table app forms.
    # Adds reusable behavior specific to the table app.

    def set_readonly(self, field_name):

        # Make a field readonly with a greyed-out style.
        if field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                "readonly": True,
                "style": "background-color: #e9ecef; font-weight: bold;",
            })

    def set_switch(self, field_name):

        # Turn a boolean field into a Bootstrap switch.
        if field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                "class": "form-check-input",
                "role": "switch",
            })
    
    def set_number(self, field_name):

        # Utility method to apply a consistent style to numeric form fields.
        if field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                "step": "0.01",
                "class": "form-control form-control-sm",
            })