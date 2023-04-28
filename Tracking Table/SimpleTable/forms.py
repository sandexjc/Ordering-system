from django import forms
import table

class SearchForm(forms.Form):

    category_choices = [
    ('All', 'All'),
    ('ID', 'ID'),
    ('Client Name', 'Client Name'),
    ('Telephone', 'Telephone'),
    ('Date', 'Date')
    ]

    category = forms.ChoiceField(choices=category_choices)
    search_field = forms.CharField(max_length=100, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_field'].label = ""
        self.fields['search_field'].widget.attrs['placeholder'] = 'Search here...'
        self.fields['category'].widget.attrs = {
        'class': 'form-select',
        }

class FilterForm(forms.Form):

    fast_select_choice = [
        (80, 'последни 80'),
        (100, 'последни 100'),
        (150, 'последни 150'),
        (300, 'последни 300'),
        (500, 'последни 500'),
        ('all', 'всички'),
    ]

    fast_select = forms.ChoiceField(widget=forms.RadioSelect, choices=fast_select_choice, initial='80')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fast_select'].label = "Виж"
        self.fields['fast_select'].widget.attrs = {
        'class': 'form-check',
        }

class UpdateOrderProgressForm(forms.ModelForm):

    class Meta:
        model = table.models.Order
        fields = ('order_taken', 'invoice',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order_taken'].widget.attrs = {
        'style': 'width: 90px; height: 30px; margin-left: auto; margin-right: auto;',
        'class': 'form-check-input',
        'role': 'checkbox',
        }
        self.fields['invoice'].widget.attrs = {
        'style': 'width: 90px; height: 30px; margin-left: auto; margin-right: auto;',
        'class': 'form-check-input',
        'role': 'checkbox',
        }

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