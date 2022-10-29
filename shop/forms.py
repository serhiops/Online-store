from django import forms
from .models import Ordering

class AddToCartForm(forms.Form):
    qty = forms.CharField(widget = forms.TextInput(attrs={
        'id':'quantity_input',
        'type':'text',
        'pattern':'^[0-9]+$',
        'value':'1',
    }))

class CartForm(forms.ModelForm):
    qty = forms.CharField(widget=forms.TextInput(attrs={
        'id':'quantity_input',
        'type':'text',
        'pattern':'^[0-9]+$',
        'value':'1',
    }))

class MyFormSet(forms.BaseModelFormSet):
    def add_fields(self, form, index) -> None:
        form.fields['qty'].label = ''
        return super().add_fields(form, index)


class OrderingForm(forms.ModelForm):
    #payment = forms.MultipleChoiceField(choices=Ordering.TYPE_OF_PAYMENT, widget= forms.RadioSelect(attrs={
    #    'class' : 'form-control',
    #    'style' : 'color:black;'
    #}))
    class Meta:
        model = Ordering
        fields = ('first_name', 'last_name', 'city', 'post_office', 'payment', 'number_of_phone')

        widgets = {
            'first_name' : forms.TextInput(attrs={
                'id' : 'checkout_name',
                'required' : 'required',
                'class' : 'form-control black-color',
            }),
            'last_name' : forms.TextInput(attrs={
                'id' : 'checkout_last_name',
                'required' : 'required',
                'class' : 'form-control black-color',
            }),
            'city' : forms.TextInput(attrs={
                'city' : 'city',
                'list' : 'cityname',
                'class' : 'form-control black-color',
                'id' : 'checkout_city',
            }),
            'post_office' : forms.TextInput(attrs={
                'name' : 'post',
                'list' : 'postname',
                'class' : 'form-control black-color',
                'id' : 'checkout_post',
                'placeholder' : 'Введіть номер відділення або поштомату',
                'disabled' : 'disabled',
            }),
            'payment' : forms.RadioSelect(attrs={
                'class' : 'form-control black-color',
            }),
            'number_of_phone' : forms.TextInput(attrs={
                'class' : 'form-control black-color',
            })
        }

class SearchForm(forms.Form):

    text = forms.CharField(widget=forms.TextInput(attrs={
        'type' : 'text',
        'class' : 'search_input',
        'placeholder' : 'Search',
        'required' : 'required',
    }))

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=64, widget=forms.TextInput(attrs={
        'class':'form-control',
        'style' : 'color:black',
        'required' : 'required',
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class':'form-control',
        'style' : 'color:black',
        'required' : 'required',
    }))
