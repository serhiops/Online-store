from django import template
from django.db import models

register = template.Library()

@register.filter(name='getDiscountPrice')
def getDiscountPrice(value : models.Model):
    price = value.price
    if value.discount:
        price -= (price * value.discount / 100)
    return price.amount

@register.filter(name = 'getTotalPrice')
def getTotalPrice(value : models.Model, arg : int):
    price = value.price * int(arg)
    if value.discount:
        price -= (price * value.discount / 100)
    return price.amount

@register.filter(name = 'getPriceByQty')
def getPriceByQty(value : models.Model):
    return (value.product.price.amount - (value.product.price.amount * value.product.discount / 100)) * value.qty


