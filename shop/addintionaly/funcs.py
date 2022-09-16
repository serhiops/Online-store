from shop.models import Product

def getPriceByDiscount(product : Product):
    return product.price if not product.discount else product.price - (product.price * product.discount / 100)