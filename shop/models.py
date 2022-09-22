from django.contrib.auth.models import AbstractUser
from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.auth import get_user_model
from django.urls import reverse
from .addintionaly.user_manager import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail

class CustomUser(AbstractUser,PermissionsMixin):
    username = None
    email = models.EmailField('email address', unique=True)
    first_name = models.CharField('first name', max_length=30, blank=True)
    last_name = models.CharField('last name', max_length=30, blank=True)
    date_joined = models.DateTimeField('date joined', auto_now_add=True)
    is_active = models.BooleanField('active', default=True)
    is_admin = models.BooleanField('is admin', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = tuple()

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name
    
    @property
    def is_staff(self):
        return self.is_admin    
            
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

    def get_absolute_url(self):
        return reverse("shop:by_category", kwargs={"categorySlug": self.slug})
    
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

class MailingList(models.Model):
    email = models.EmailField(unique=True)

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
    in_stock = models.BooleanField(default=True, verbose_name='in stock')
    
    class Meta:
        ordering = ("-created",)

    def get_absolute_url(self) -> str:
        return reverse('shop:detail_product', kwargs={'productSlug': self.slug, 'categorySlug':self.category.slug})
    
    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        send_mail(
            'Повідомлення від інтернет-магазину.',
            'На сайті з\'явився новий товар в категорії "%s" : %s.' % (self.category.name, self.name),
            from_email = None,
            *MailingList.objects.values_list('email')
        )
        return super().save(*args, **kwargs)

class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name="cartListProduct", verbose_name="product")
    added = models.DateTimeField(auto_now_add=True, verbose_name="added")
    qty = models.PositiveIntegerField(default=1, verbose_name="qty")
    user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, related_name="cartListUser")
    class Meta:
        ordering = ("-added",)

class Ip(models.Model):
    ip = models.CharField(max_length=100)

    def __str__(self):
        return self.ip

class TempOrdering(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="get_pr", verbose_name="product")
    qty = models.PositiveIntegerField(default=1, verbose_name="qty")
    current_price = MoneyField(max_digits=14, decimal_places=2, default_currency='UAH', verbose_name="price")
    created = models.DateTimeField(auto_now_add=True, verbose_name="created")
    main_ordering = models.ForeignKey('Ordering', on_delete=models.CASCADE, related_name='tempOrderingList')

    class Meta:
        ordering = ("-created",)

class Ordering(models.Model):

    MASTERCARD = 'MC'
    PAYPAL = 'PP'
    CASH_ON_DELAVERY = 'COD'
    CREDIT_CARD = 'CC'
    DIRECT_BANK_TRANSFER = 'DBT'

    TYPE_OF_PAYMENT = [
        (MASTERCARD, 'Mastercard'),
        (PAYPAL, 'Paypal'),
        (CASH_ON_DELAVERY, 'Cash on delivery'),
        (CREDIT_CARD, 'Credit card'),
        (DIRECT_BANK_TRANSFER, 'Direct bank transfer')
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="get_user", verbose_name="buyer")
    first_name = models.CharField(max_length=32, blank = True)
    last_name = models.CharField(max_length=32, blank = True)
    city = models.CharField(max_length=50, blank = True)
    number_of_phone = models.CharField(max_length=15, verbose_name='number of phone', blank=True)
    post_office = models.CharField(max_length=64, blank = True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="created")
    payment = models.CharField(default=DIRECT_BANK_TRANSFER, choices=TYPE_OF_PAYMENT, max_length=3, blank = True)
    is_done = models.BooleanField(default=False, verbose_name='is done')
    total_price = MoneyField(max_digits=14, decimal_places=2, default_currency='UAH', verbose_name="price", blank = True, null=True)  #del


User = get_user_model()

