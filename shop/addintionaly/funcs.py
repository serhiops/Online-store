from shop.models import Product
from django.forms import BaseForm

def getErrorMessageString(form : BaseForm) -> str:
    return "Error!"

def getPriceByDiscount(product : Product):
    return product.price if not product.discount else product.price - (product.price * product.discount / 100)