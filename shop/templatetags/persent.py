from django import template
from shop.models import Product

register = template.Library()

@register.filter(name='getDiscountPrice')
def getDiscountPrice(value : Product):
    price = value.price
    if value.discount:
        price -= (price * value.discount / 100)
    return price.amount

@register.filter(name = 'getTotalPrice')
def getTotalPrice(value : Product, arg : int):
    price = value.price * int(arg)
    if value.discount:
        price -= (price * value.discount / 100)
    return price.amount



