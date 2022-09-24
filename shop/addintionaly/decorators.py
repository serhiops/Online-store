from functools import wraps
from django.http import JsonResponse
from typing import Callable

def errorJsonResponse(function : Callable):
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except Exception as _ex:
            return JsonResponse({ 'success' : False, 'message' : 'Виникла помилка! Ви можете повідомити про це адміністратора.' })
    return wrapper

