from django import forms
import table

class SearchForm(forms.Form):
    search_field = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_field'].label = ""
        self.fields['search_field'].widget.attrs['placeholder'] = 'Search here...'

class UpdatePlateProgressForm(forms.ModelForm):

    class Meta:
        model = table.models.Plate
        fields = (
            'ordered', 'delivered',
            'cutted', 'edged',
            'material', 'manufacturer',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ordered'].widget.attrs = {
        'style': 'width: 90px; height: 30px; margin-left: auto; margin-right: auto;',
        'class': 'form-check-input',
        'role': 'checkbox',
        }
        self.fields['delivered'].widget.attrs = {
        'style': 'width: 90px; height: 30px',
        'class': 'form-check-input',
        'role': 'checkbox',
        }
        self.fields['cutted'].widget.attrs = {
        'style': 'width: 90px; height: 30px',
        'class': 'form-check-input',
        'role': 'checkbox',
        }
        self.fields['edged'].widget.attrs = {
        'style': 'width: 90px; height: 30px',
        'class': 'form-check-input',
        'role': 'checkbox',
        }
        self.fields['material'].widget.attrs = {
        'style': 'width: 90px; height: 30px',
        'class': 'form-control-plaintext',
        'readonly': True,
        }
        self.fields['material'].required = False
        self.fields['manufacturer'].required = False

class UpdateEdgeProgressForm(forms.ModelForm):

    class Meta:
        model = table.models.Edge
        fields = (
            'ordered', 'delivered',
            'color_code', 'edge_type',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ordered'].widget.attrs = {
        'style': 'width: 40px; height: 40px;',
        'class': 'form-check-input',
        'role': 'checkbox',
        }
        self.fields['delivered'].widget.attrs = {
        'style': 'width: 40px; height: 40px;',
        'class': 'form-check-input',
        'role': 'checkbox',
        }
        self.fields['color_code'].widget.attrs = {
        'style': 'width: 90px; height: 30px',
        'class': 'form-control-plaintext',
        }
        self.fields['edge_type'].widget.attrs = {
        'style': 'width: 90px; height: 30px',
        'class': 'form-control-plaintext',
        }


PlateProgressFormSet = forms.inlineformset_factory(
        table.models.Order,
        table.models.Plate,
        form=UpdatePlateProgressForm,
        extra=0,
        can_delete=False,
    )

EdgeProgressFormSet = forms.inlineformset_factory(
        table.models.Order,
        table.models.Edge,
        form=UpdateEdgeProgressForm,
        extra=0,
        can_delete=False,
    )