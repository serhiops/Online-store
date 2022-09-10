from django.forms import BaseForm
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from shop.models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def getErrorMessageString(form : BaseForm) -> str:
    print(form.errors)
    return "Error!"


def sendVerifyEmail(request : HttpResponse, user : CustomUser):
    currentSite = get_current_site(request)

    context = {
        'user' : user,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        'domain' : currentSite.domain,
        'token': default_token_generator.make_token(user),
        'protocol' : 'http',    #не забыть поменять
    }

    message = loader.render_to_string('authentication/authentication/verify_email.html', context)

    email = EmailMessage('Verify email', message, to=[user.email])

    email.send()