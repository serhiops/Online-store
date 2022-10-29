from django.shortcuts import redirect
from django.contrib import messages
from shop.addintionaly.funcs import getErrorMessageString
from shop.mixins import BaseMixin
from allauth.account.views import (
    LoginView as AllauthLoginView,
    SignupView as AllauthSignupView,
    PasswordResetFromKeyView as AllauthPasswordResetFromKeyView
)


def redirectAfterPasswordReset(request):
    messages.success(request, 'Ви успішно змінили пароль!')
    return redirect('account_login')

class AuthMixin(BaseMixin):
    def form_invalid(self, form):
        messages.error(self.request, getErrorMessageString(form))
        return super().form_invalid(form)

class LoginView(AuthMixin, AllauthLoginView):
    pass

class SignupView(AuthMixin, AllauthSignupView):
    pass

class PasswordResetFromKeyView(AuthMixin,AllauthPasswordResetFromKeyView):
    pass