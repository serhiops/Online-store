from django import forms
from django.contrib.auth.forms import UserCreationForm
from shop.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .addintionaly.funcs import sendVerifyEmail
from django.contrib.auth import  authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    class Meta(UserCreationForm):
        model = User
        fields = ('email', 'number_of_phone')
        widgets = {
            'email' : forms.EmailInput(attrs={
                'class' : 'form-control',
            }),
            'number_of_phone': forms.TextInput(
                attrs={
                'class' : 'form-control',
            })
        }
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
        

class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_admin')



class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class' : 'contact_input',}))  #this is an email field, not a username
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'contact_input',}))

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email is not None and password:

            self.user_cache = authenticate(
                self.request, username = email, password = password
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

class ChangeUserDataForm(forms.ModelForm):

    class Meta:
        model  = User
        fields = ('number_of_phone',  'email')
        widgets = {
            'number_of_phone' : forms.TextInput(attrs={
                'class' : 'form-control',
                'style':'color:black'
            }),
            
            'email' : forms.EmailInput(attrs={
                'class' : 'form-control',
                'style':'color:black'
            })
        }