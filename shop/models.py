from django.contrib.auth.models import AbstractUser
from django.db import models
from djmoney.models.fields import MoneyField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.urls import reverse

class CustomUser(AbstractUser):
    number_of_phone = models.CharField(_('number of phone'), max_length=15, blank=True, null=True)
    email_verify = models.BooleanField(_('is verify email'), default=False)

class Category(models.Model):
    name = models.CharField(_('name'), max_length=64)
    description = models.CharField(_('description'), max_length=128)
    slug = models.SlugField(_('URL'),max_length=64,unique=True)
    is_active = models.BooleanField(_('active'), default=True)
    image = models.ImageField(_('image'), upload_to="images/categories/%Y/%m/%d")
    
    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name

class Review(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='get_author', verbose_name=_('author') )
    text = models.TextField(_('text'), max_length=1024)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    is_active = models.BooleanField(_('active'), default=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='get_prd', verbose_name=_('product'))

    class Meta:
        ordering = ('-created',)

    def __str__(self) -> str:
        return self.author.username

class Photo(models.Model):
   image = models.ImageField(_('image'), upload_to="images/products/%Y/%m/%d")
   product = models.ForeignKey('Product',on_delete=models.CASCADE, related_name='photos', verbose_name=_('product'))

class Product(models.Model):
    name = models.CharField(_('name'), max_length=64)
    description = models.TextField(_('description'))
    price = MoneyField(_('price'), max_digits=14, decimal_places=2, default_currency='UAH')
    is_active = models.BooleanField(_('active'), default=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)
    slug = models.SlugField(_('URL'),max_length=64,  unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name = 'get_category', verbose_name=_('category'))
    views = models.ManyToManyField("Ip", related_name='post_views', blank=True, verbose_name=_('views'))
    discount = models.PositiveIntegerField(_('sale'), default=0)
    
    class Meta:
        ordering = ("-created",)

    def get_absolute_url(self) -> str:
        return reverse('shop:detail_product', kwargs={'productSlug': self.slug, 'categorySlug':self.category.slug})
    

    def __str__(self) -> str:
        return self.name

class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name="get_product", verbose_name=_('product'))
    added = models.DateTimeField(_('added'), auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, verbose_name=_('user'))
    class Meta:
        ordering = ("-added",)

class Ip(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip

class Ordering(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="get_user",verbose_name=_('buyer'))
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="get_pr", verbose_name=_('product'))
    qty = models.PositiveIntegerField(_('qty'), default=1)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    class Meta:
        ordering = ("-created",)


User = get_user_model()