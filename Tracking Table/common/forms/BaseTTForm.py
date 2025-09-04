from django import forms

class BaseForm(forms.ModelForm):
    
    # Top level form for the whole project.
    # Defines common widget styling and helper logic.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply default bootstrap class to all fields
        for field_name, field in self.fields.items():
            css_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{css_class} form-control form-control-sm".strip()

    class Meta:
        abstract = True