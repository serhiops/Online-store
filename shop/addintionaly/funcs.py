from shop.models import Product
from django.forms import BaseForm

def getErrorMessageString(form : BaseForm) -> str:
    return form.errors.as_text()

def getPriceByDiscount(product : Product):
    return product.price if not product.discount else product.price - (product.price * product.discount / 100)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_filename(filename : str):
    """ for CKEditor """
    return filename.upper()