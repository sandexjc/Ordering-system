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
    
    def set_lg_checkbox(self, field_name):

        # Turn a boolean field into large Bootstrap checkbox
        if field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'style': 'width: 6rem; height: 2rem;',
                'class': 'form-check-input mx-auto d-block',
                'role': 'checkbox',
            })
    
    def set_sm_checkbox(self, field_name):

        # Turn a boolean field into small Bootstrap checkbox
        if field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'style': 'width: 2.5rem; height: 2.5rem;',
                'class': 'form-check-input mx-auto d-block',
                'role': 'checkbox',
            })
    
    def set_number(self, field_name):

        # Utility method to apply a consistent style to numeric form fields.
        if field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                "step": "0.01",
                "class": "form-control form-control-sm",
            })