from django.forms import ModelForm, inlineformset_factory
from django import forms
from table import models

class CreateOrderForm(ModelForm):

    class Meta:
        model = models.Order
        fields = ('owner', 'telephone', 'client',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].widget.attrs['placeholder'] = 'Name'
        self.fields['owner'].label = 'Client Name'

class UpdateOrderForm(ModelForm):

    class Meta:
        model = models.Order
        fields = (
            'ID', 'created_date', 'owner',
            'client', 'telephone'
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].widget.attrs = {
        'placeholder': 'Client Name',
        'readonly': False,
        }    
        self.fields['owner'].label = 'Client Name'
        self.fields['created_date'].widget.attrs['readonly'] = False

class AddNoteForm(ModelForm):

    class Meta:
        model = models.Note
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs = {
        'cols': 5,
        'rows': 3,
        'placeholder': 'Add Note..'
        }
        self.fields['content'].label = 'Notes'

class AddPlateForm(ModelForm):

    class Meta:
        model = models.Plate
        fields = (
            'material', 'manufacturer', 'from_client',
            'quantity', 'price', 'value',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].widget.attrs = {
        'style': 'width: 150px;', 
        'class': 'form-control form-control-sm',
        }
        self.fields['manufacturer'].widget.attrs = {
        'style': 'width: 120px',  
        'class': 'form-select form-select-sm'
        }
        self.fields['from_client'].widget.attrs = {
        'style':'width: 30px; height: 15px;',
        'class': 'form-check-input',
        'role': 'switch',
        }
        self.fields['quantity'].widget.attrs = {
        'style': 'width: 90px', 
        'class': 'form-control form-control-sm'
        }
        self.fields['price'].widget.attrs = {
        'style': 'width: 90px', 
        'step': '0.01', 
        'class': 'form-control form-control-sm'
        }
        self.fields['value'].widget.attrs = {
        'readonly': 'True', 
        'style': 'background-color: #e9ecef; width: 110px; font-weight: bold;', 
        'class': 'form-control form-control-sm'
        }

class AddCuttingForm(ModelForm):

    class Meta:
        model = models.Cutting
        fields = (
            'cutting_type', 'quantity',
            'price', 'value',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cutting_type'].widget.attrs = {
        'style': 'width: 200px', 
        'class': 'form-control form-control-sm'
        }
        self.fields['quantity'].widget.attrs = {
        'style': 'width: 75px', 
        'class': 'form-control form-control-sm'
        }
        self.fields['price'].widget.attrs = {
        'style': 'width: 100px', 
        'step': '0.01', 
        'class': 'form-control form-control-sm'}
        self.fields['value'].widget.attrs = {
        'readonly': 'True', 
        'style': 'background-color: #e9ecef; width: 190px; font-weight: bold;', 
        'class': 'form-control form-control-sm'}


class AddEdgeForm(ModelForm):

    class Meta:
        model = models.Edge
        fields = (
            'edge_type', 'color_code',
            'quantity', 'price', 'value',
            'visible',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['edge_type'].widget.attrs = {
        'style': 'width: 100px', 
        'class': 'form-control form-control-sm'
        }
        self.fields['color_code'].widget.attrs = {
        'style': 'width: 80px', 
        'class': 'form-control form-control-sm'
        }
        self.fields['quantity'].widget.attrs = {
        'style': 'width: 80px', 
        'class': 'form-control form-control-sm'
        }
        self.fields['price'].widget.attrs = {
        'style': 'width: 100px', 
        'step': '0.01', 
        'class': 'form-control form-control-sm'
        }
        self.fields['value'].widget.attrs = {
        'readonly': 'True', 
        'style': 'background-color: #e9ecef; font-weight: bold; width: 150px;', 
        'class': 'form-control form-control-sm',
        }
        self.fields['visible'].widget.attrs = {
        'style':'width: 30px; height: 15px;',
        'class': 'form-check-input',
        'role': 'switch'
        }


class AddEdgingForm(ModelForm):

    class Meta:
        model = models.Edging
        fields = (
            'edging_type', 'quantity',
            'price', 'value',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['edging_type'].widget.attrs = {
        'style': 'width: 200px', 
        'class': 'form-control form-control-sm'
        }
        self.fields['quantity'].widget.attrs = {
        'style': 'width: 75px', 
        'class': 'form-control form-control-sm'
        }
        self.fields['price'].widget.attrs = {
        'style': 'width: 100px', 
        'step': '0.01', 
        'class': 'form-control form-control-sm'
        }
        self.fields['value'].widget.attrs = {
        'readonly': 'True', 
        'style': 'background-color: #e9ecef; width: 190px; font-weight: bold;', 
        'class': 'form-control form-control-sm'
        }

class AddOtherForm(ModelForm):

    class Meta:
        model = models.Other
        fields = (
            'description', 'quantity',
            'price', 'value',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs = {
        'style': 'width: 200px', 
        'class': 'form-control form-control-sm'
        }
        self.fields['quantity'].widget.attrs = {
        'style': 'width: 75px', 
        'class': 'form-control form-control-sm'
        }
        self.fields['price'].widget.attrs = {
        'style': 'width: 100px', 
        'step': '0.01', 
        'class': 'form-control form-control-sm'
        }
        self.fields['value'].widget.attrs = {
        'readonly': 'True', 
        'style': 'background-color: #e9ecef; font-weight: bold; width: 190px;', 
        'class': 'form-control form-control-sm',
        }

class AddPaymentForm(ModelForm):

    class Meta:
        model = models.Payment
        fields = (
            'payment_method', 'value',
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].widget.attrs = {
        'class': 'form-select form-select-sm',
        #'style': 'width: 80px',
        }

        self.fields['value'].widget.attrs = {
        'class': 'form-control form-control-sm',
        'style': 'width: 150px;',
        'step': '0.01',
        }

class CustomInlineFormSet(forms.BaseInlineFormSet):
    deletion_widget = forms.CheckboxInput(attrs={
        'style':'width: 30px; height: 15px;',
        'class': 'form-check-input',
        'role': 'switch'
        })

PlateFormSet = inlineformset_factory(
        models.Order, 
        models.Plate,
        formset=CustomInlineFormSet,
        form=AddPlateForm, 
        extra=3,
        can_delete_extra=False
    )

CuttingFormSet = inlineformset_factory(
        models.Order, 
        models.Cutting,
        formset=CustomInlineFormSet,
        form=AddCuttingForm, 
        extra=3,
        can_delete_extra=False
    )

EdgeFormSet = inlineformset_factory(
        models.Order, 
        models.Edge,
        formset=CustomInlineFormSet,
        form=AddEdgeForm, 
        extra=3,
        can_delete_extra=False
    )

EdgingFormSet = inlineformset_factory(
        models.Order, 
        models.Edging,
        formset=CustomInlineFormSet,
        form=AddEdgingForm, 
        extra=3,
        can_delete_extra=False
    )

OthersFormSet = inlineformset_factory(
        models.Order, 
        models.Other,
        formset=CustomInlineFormSet,
        form=AddOtherForm, 
        extra=3,
        can_delete_extra=False
    )

PaymentFormSet = inlineformset_factory(
        models.Order, 
        models.Payment,
        formset=CustomInlineFormSet,
        form=AddPaymentForm, 
        extra=1,
        can_delete_extra=False
    )