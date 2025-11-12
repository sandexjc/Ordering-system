

class FormFieldsStyleMixin:

    """ Mixin that provides helper methods for styling and controlling form fields. """

    def is_valid(self):
        # --- Lifecycle override to apply error styling automatically ---
        valid = super().is_valid()
        if not valid:
            self.apply_error_styling()
        return valid

    def apply_bootstrap_styling(self):
        # Apply default Bootstrap classes to all fields.
        for field_name, field in self.fields.items():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_class} form-control form-control-sm".strip()

    # --- Field styling helpers ---

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
    
    def set_not_required(self, field_name):
        # Set not required field
        if field_name in self.fields:
            self.fields[field_name].required = False
    
    def set_sm_dropdown(self, field_name):
        # Set small dropdown selective menu with notes of gray color
        if field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                "style": "background-color: #faf9f9",
                "class": "form-select form-select-sm",
            })
    
    def disable_if(self, condition: bool, field_name: str, reason: str | None = None):
        # Disable a field if a given condition is True.
        # Optionally adds a reason as help_text.
        
        if condition and field_name in self.fields:
            field = self.fields[field_name]
            field.disabled = True

            if reason:
                field.help_text = reason
            
            # Preserve any existing style
            current_style = field.widget.attrs.get("style", "")
            new_style = f"{current_style} background-color: #e9ecef; opacity: 0.75;"
            
            field.widget.attrs.update({
                "style": new_style.strip(),
                "title": reason or "This field is disabled",
            })
    
    def apply_error_styling(self):
        # Apply 'is-invalid' class and width-based adjustments to invalid fields.
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs.update({
                    "class": "form-control form-control-sm is-invalid",
                })
