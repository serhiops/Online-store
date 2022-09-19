from django.shortcuts import redirect
from django.contrib import messages

def redirectAfterPasswordReset(request):
    messages.success(request, 'Ви успішно змінили пароль!')
    return redirect('account_login')