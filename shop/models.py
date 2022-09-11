from django.contrib.auth.models import AbstractUser
from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.auth import get_user_model
from django.urls import reverse

class CustomUser(AbstractUser):
    number_of_phone = models.CharField(max_length=15, verbose_name='number of phone', blank=True, null=True)
    email_verify = models.BooleanField(default=False, verbose_name='is verify email')

class Category(models.Model):
    name = models.CharField(max_length=64, verbose_name="name")
    description = models.CharField(max_length=128,verbose_name="description")
    slug = models.SlugField(max_length=64, verbose_name="URL",unique=True)
    is_active = models.BooleanField(default=True, verbose_name='active')
    image = models.ImageField(upload_to="images/categories/%Y/%m/%d", verbose_name="image" )
    
    class Meta:
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name

class Review(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="get_author", verbose_name="author")
    text = models.TextField(max_length=1024, verbose_name="text")
    created = models.DateTimeField(auto_now_add=True, verbose_name="created")
    updated = models.DateTimeField(auto_now=True, verbose_name="updated")
    is_active = models.BooleanField(default=True, verbose_name="active")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="get_prd", verbose_name="product")

    class Meta:
        ordering = ('-created',)

    def __str__(self) -> str:
        return self.author.username

class Photo(models.Model):
   image = models.ImageField(upload_to="images/products/%Y/%m/%d", verbose_name="image")
   product = models.ForeignKey("Product",on_delete=models.CASCADE, related_name='photos')

class Product(models.Model):
    name = models.CharField(max_length=64, verbose_name="name")
    description = models.TextField(verbose_name="description")
    price = MoneyField(max_digits=14, decimal_places=2, default_currency='UAH', verbose_name="price")
    is_active = models.BooleanField(default=True, verbose_name="active")
    created = models.DateTimeField(auto_now_add=True, verbose_name="created")
    updated = models.DateTimeField(auto_now=True, verbose_name="updated")
    slug = models.SlugField(max_length=64, verbose_name="URL", unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,related_name = "get_category", verbose_name="category")
    views = models.ManyToManyField("Ip", related_name="post_views", blank=True)
    discount = models.PositiveIntegerField(default=0, verbose_name='sale')
    
    class Meta:
        ordering = ("-created",)

    def get_absolute_url(self) -> str:
        return reverse('shop:detail_product', kwargs={'productSlug': self.slug, 'categorySlug':self.category.slug})
    

    def __str__(self) -> str:
        return self.name

class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name="get_product", verbose_name="product")
    added = models.DateTimeField(auto_now_add=True, verbose_name="added")
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, related_name="get_fp")
    class Meta:
        ordering = ("-added",)

class Ip(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip

class Ordering(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="get_user", verbose_name="buyer")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="get_pr", verbose_name="product")
    qty = models.PositiveIntegerField(default=1, verbose_name="qty")
    created = models.DateTimeField(auto_now_add=True, verbose_name="created")
    class Meta:
        ordering = ("-created",)


User = get_user_model()