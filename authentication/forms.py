from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from shop.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .addintionaly.funcs import sendVerifyEmail
from django.contrib.auth import  authenticate

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    class Meta(UserCreationForm):
        model = User
        fields = ('username', 'email', 'number_of_phone')
        widgets = {
            'username':forms.TextInput(attrs={
                'class' : 'form-control',
            }),
            'email' : forms.EmailInput(attrs={
                'class' : 'form-control',
            }),
            'number_of_phone': forms.NumberInput(
                attrs={
                'class' : 'form-control',
            })
        }
    def clean_email(self):
        _email = self.changed_data['email']
        if User.objects.filter(email = _email):
            raise ValidationError('Ця пошта вже зайнята!')
        return _email
        

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username', 'email')



class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'contact_input',}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'contact_input',}))

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            elif not self.user_cache.email_verify:
                sendVerifyEmail(self.request, self.user_cache)
                raise ValidationError(
                    'Користувач не підтвердив електронну пошту!',
                    code="invalid_login",
                    params={"username": self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data