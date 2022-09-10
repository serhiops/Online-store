from django import template

register = template.Library()

@register.filter(name='getDiscountPrice')
def getDiscountPrice(value, arg):
    return value - (value * arg / 100) if 0 < arg < 100 else value

