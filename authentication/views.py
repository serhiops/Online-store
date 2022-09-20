from django.shortcuts import redirect
from django.contrib import messages
from allauth.account.views import LoginView as AllauthLoginView, SignupView as AllauthSignupView
from shop.addintionaly.funcs import getErrorMessageString

def redirectAfterPasswordReset(request):
    messages.success(request, 'Ви успішно змінили пароль!')
    return redirect('account_login')

class LoginView(AllauthLoginView):

    def form_invalid(self, form):
        messages.error(self.request, getErrorMessageString(form))
        return super().form_invalid(form)

class SignupView(AllauthSignupView):

    def form_invalid(self, form):
        messages.error(self.request, getErrorMessageString(form))
        return super().form_invalid(form)

