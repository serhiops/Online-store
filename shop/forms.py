from django import forms
from .models import Cart

class AddToCartForm(forms.Form):
    qty = forms.CharField(widget = forms.TextInput(attrs={
        'id':'quantity_input',
        'type':'text',
        'pattern':'[0-9]',
        'value':'1',
    }))

class CartForm(forms.ModelForm):
    qty = forms.CharField(widget=forms.TextInput(attrs={
        'id':'quantity_input',
                'type':'text',
                'pattern':'[0-9]',
                'value':'1',
    }))
    class Meta:
        model = Cart
        fields  = ['qty',]
        widgets = {
            'qty' : forms.CharField(widget = forms.TextInput(attrs={
                'id':'quantity_input',
                'type':'text',
                'pattern':'[0-9]',
                'value':'1',
            }))
        }

class MyFormSet(forms.BaseModelFormSet):
    def add_fields(self, form, index) -> None:
        form.fields['qty'].label = ''
        return super().add_fields(form, index)

