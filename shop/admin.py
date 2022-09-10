from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authentication.forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Category, Review, Product, Cart, Ip, Ordering, Photo

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username', 'email_verify')
    list_editable = ('email_verify',)
    list_display_links = ('email','username')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    list_filter = ('name',)
    search_fields = ('name', )
    prepopulated_fields = {'slug' : ('name',)}

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'created', 'updated', 'is_active')
    list_display_links = ('author', 'product',)
    list_filter = ('created', 'updated')
    search_fields = ('created', 'updated' )

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created', 'updated','is_active' )
    list_display_links = ('name', 'price',)
    list_filter = ('created', 'updated' ,'price', 'views')
    search_fields = ('created', 'updated','price', 'views' )
    prepopulated_fields = {'slug' : ('name',),}

class CartAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'added')
    list_display_links = ('product', 'user',)
    list_filter = ('added',)
    search_fields = ('added',)

class IpAdmin(admin.ModelAdmin):
    list_display = ('ip',)
    list_display_links = ('ip',)

class OrderingAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'qty', 'created')
    list_display_links = ('user', 'product',)
    list_filter = ('created',)
    search_fields = ('created', )    

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id',)

admin.site.register(Photo, PhotoAdmin)
admin.site.register(Ordering, OrderingAdmin)
admin.site.register(Ip, IpAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
