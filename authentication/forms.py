from django import forms
from shop.models import User, Product, Cart
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from allauth.account.forms import (
    LoginForm as AllauthLoginForm, 
    SignupForm as AllauthSignupForm,
    ResetPasswordForm as AllauthResetPasswordForm,
    ResetPasswordKeyForm as AllauthResetPasswordKeyForm
)
from allauth.socialaccount.forms import SignupForm as AllauthSocialAccountSignupForm

class LoginForm(AllauthLoginForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget = forms.EmailInput(attrs={
            'class' : 'contact_input',
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class' : 'contact_input',
        })

    def login(self, *args, **kwargs):
        """ Якщо у сесії незареєстрованого користувача є товари в клшику, тоді додаємо їх до бази данних """
        ret =  super().login(*args, **kwargs)
        data : dict = self.request.session.get('cart_pk_list', {})
        if data:
            products = Product.objects.filter(pk__in = data.keys())
            Cart.objects.filter(product__in = Product.objects.filter(pk__in = data.keys()),
                                user = self.request.user).delete()
            
            cartList = list()
            for product_id, qty in data.items():
                cartList.append(Cart(
                    user = self.request.user,
                    product = products.get(pk = product_id),
                    qty = qty
                ))
            Cart.objects.bulk_create(cartList)

        return ret

class SignupForm(AllauthSignupForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class':'form-control',
            'style' : 'color:black',
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class':'form-control',
            'style' : 'color:black',
        })
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class':'form-control',
            'style' : 'color:black',
        })

class SocialAccountSignupForm(AllauthSocialAccountSignupForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class':'contact_input',
        })

class ResetPasswordForm(AllauthResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = forms.EmailInput(attrs={
            'placeholder' : 'example@gmail.com',
            'class' : 'form-control',
            'style' : 'color:black',
        })

class ResetPasswordKeyForm(AllauthResetPasswordKeyForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class' : 'form-control',
            'style' : 'color:black'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class' : 'form-control',
            'style' : 'color:black'
        })

class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_admin')
