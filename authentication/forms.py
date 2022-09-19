from django import forms
from shop.models import User
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
            'class' : 'contact_input ',
        })
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'class' : 'contact_input',
        })

class SignupForm(AllauthSignupForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class':'form-control',
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class':'form-control',
        })
        self.fields['email'].widget = forms.EmailInput(attrs={
            'class':'form-control',
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
