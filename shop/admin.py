from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from authentication.forms import CustomUserChangeForm, SignupForm

from .models import CustomUser, Category, Review, Product, Cart, Ip, TempOrdering, Photo, Ordering

class CustomUserAdmin(UserAdmin):
    add_form = SignupForm
    form = CustomUserChangeForm
    model = CustomUser
    readonly_fields = ('date_joined',)
    list_display = ('email',  )
    list_display_links = ('email',)
    ordering = ('email',)
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    search_fields = ('email',)
    ordering = ('email',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

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

class TempOrderingAdmin(admin.ModelAdmin):
    list_display = ('product','main_ordering','created',)
    list_filter = ('product', 'main_ordering','created',)
    search_fields = ('created',)    

class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id',)

class OrderingAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name')
    list_display_links = ('user', 'first_name', 'last_name')

admin.site.register(Photo, PhotoAdmin)
admin.site.register(TempOrdering, TempOrderingAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Ordering, OrderingAdmin)

admin.site.register(Ip, IpAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CustomUser, CustomUserAdmin)


admin.site.unregister(Group)