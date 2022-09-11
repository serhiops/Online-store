from django import forms
from .models import Cart

class AddToCartForm(forms.Form):
    qty = forms.CharField(widget = forms.TextInput(attrs={
        'id':'quantity_input',
        'type':'text',
        'pattern':'[0-9]',
        'value':'1',
    }))

class CartForm(forms.Form):

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

