from functools import wraps
from django.http import JsonResponse
from typing import Callable
import logging
from django.http import HttpRequest
from django.shortcuts import redirect

def errorJsonResponse(function : Callable):
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except Exception as _ex:
            return JsonResponse({ 'success' : False, 'message' : 'Виникла помилка! Ви можете повідомити про це адміністратора.' })
    return wrapper

def accessIfCartNotEmpty(reverse_url, level:logging = logging.DEBUG):
    def decorate(foo):
        log = logging.getLogger(foo.__module__)
        logmsg = foo.__name__
        @wraps(foo)
        def wrapper(request : HttpRequest, *args, **kwargs):
            log.log(level, logmsg)
            if not ((request.user.is_authenticated and request.user.cartListUser.all().exists()) or (request.user.is_anonymous and request.session.get('cart_pk_list', False))):
                return redirect(reverse_url)
            return foo(request, *args, **kwargs)
        return wrapper
    return decorate
