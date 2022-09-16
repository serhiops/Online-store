from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from . import forms
from django.contrib import messages
from django.contrib.auth import logout, login
from django.views.generic import FormView
from .addintionaly.funcs import getErrorMessageString, sendVerifyEmail
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User as _User
from django.contrib.auth.tokens import default_token_generator
from shop.models import User
from django.contrib.messages.views import SuccessMessageMixin
from shop.mixins import BaseMixin

class EmailVerify(View):

    def get(self, request :HttpRequest ,uidb64 : str, token : str) -> HttpResponse:
        user = self.get_user(uidb64)
        if user is not None and default_token_generator.check_token(user, token):
            user.email_verify = True
            user.save()
            login(request, user,  backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Ви упішно зареєструвалися!')
            return redirect('shop:index')

        messages.error(request, 'Помилка :(')
        return redirect('shop:index')

    def get_user(self, uidb64 : str) -> None or _User:
        """ Copied from django/contrib/auth/views.py class PasswordResetConfirmView """
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user

class Login(LoginView, BaseMixin):
    template_name = 'authentication/authentication/login.html'
    form_class = forms.LoginForm

    def form_valid(self, form : AuthenticationForm) -> HttpResponse:
        messages.success(self.request,'Ви успішно увійшли до облікового запису!')
        return super().form_valid(form)
    
    def form_invalid(self, form : AuthenticationForm) -> HttpResponse:
        messages.error(self.request, form.errors.as_text() )
        return super().form_invalid(form)
    

class Register(FormView, BaseMixin):
    template_name = 'authentication/authentication/register.html'
    form_class = forms.CustomUserCreationForm
    success_url = reverse_lazy('authentication:confirm_email')

    def form_valid(self, form : UserCreationForm) -> HttpResponse:
        user = form.save()
        sendVerifyEmail(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form : UserCreationForm) -> HttpResponse:
        messages.error(self.request, getErrorMessageString(form))
        return super().form_invalid(form)
    

def logoutUser(request):
    logout(request)
    messages.success(request, 'Ви вийшли зі свого облікового запису!')
    return redirect('shop:index')

class PasswordReset(PasswordResetView):
    template_name = 'authentication/password_reset/password_reset_form.html'
    subject_template_name = 'authentication/password_reset/password_reset_subject.html'
    email_template_name = 'authentication/password_reset/password_reset_email.html'
    html_email_template_name = None
    success_url = reverse_lazy('authentication:password_reset_done')

    def get_form(self, *args, **kwargs):
        form =  super().get_form(*args, **kwargs)
        form.fields["email"].widget.attrs["class"] = "form-control"
        return form 

class PasswordResetConfirm(SuccessMessageMixin, PasswordResetConfirmView):
    template_name = 'authentication/password_reset/password_confirm.html'
    success_url = reverse_lazy('authentication:login')
    success_message = 'Ви успішно змінили пароль!'

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields["new_password1"].widget.attrs["class"] = "contact_input"
        form.fields["new_password2"].widget.attrs["class"] = "contact_input"
        return form
