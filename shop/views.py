from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import Category, Product, Cart, Ordering
from django.views.generic import ListView, DetailView, FormView
from . import forms
from django.urls import reverse_lazy
from django.contrib import messages
from django.forms import Form, modelformset_factory
from .mixins import BaseMixin

def index(request : HttpRequest) -> HttpResponse:
    categories = Category.objects.filter(is_active = True)
    products = Product.objects.filter(is_active = True)[:8]  
    context = {
        'categories' : categories,
        'products' : products,
    }
    return render(request, 'shop/index.html', context)

class ByCategory(ListView, BaseMixin):
    template_name = 'shop/product/by_category.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(category__slug = self.kwargs['categorySlug'], is_active = True)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['currentCategory'] = Category.objects.get(slug = self.kwargs['categorySlug'])
        return context
   

class DetailProduct(DetailView, FormView, BaseMixin):
    model = Product
    form_class = forms.AddToCartForm
    template_name = 'shop/product/detail_product.html'
    slug_url_kwarg = 'productSlug'
    context_object_name = 'product'
    success_url = reverse_lazy('shop:cart')

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['currentCategory'] = Category.objects.get(slug = self.kwargs['categorySlug'])
        context['relatedProducts'] = Product.objects.filter(is_active = True).order_by('?')[:4]
        return context

    def form_valid(self, form : Form) -> HttpResponse:
        product = self.get_object()
        cart_pk_list = self.request.session.get('cart_pk_list', {})
        if cart_pk_list.get(str(product.pk), False):
            del cart_pk_list[str(product.pk)]
        cart_pk_list[product.pk] = form.cleaned_data.get('qty', 0)
        self.request.session['cart_pk_list'] = cart_pk_list
        if self.request.user.is_authenticated:
            cart = Cart.objects.filter(product = product, user = self.request.user)
            if cart:
                [x.delete() for x in cart]
            Cart.objects.create(product = product, user = self.request.user, qty = form.cleaned_data.get('qty', 1))
        messages.success(self.request, 'Ви успішно додали товар до кошика!')
        return super().form_valid(form)

    def form_invalid(self, form: Form) -> HttpResponse:
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)


def cartView(request : HttpRequest) -> HttpResponse:
    products = list()
    context = dict()
    if request.user.is_authenticated:
 
        products = request.user.cartListUser.all() 
        CartFormSet = modelformset_factory( 
                                            model = Cart, fields = ('qty', ), 
                                            extra = 0, formset = forms.MyFormSet, 
                                            form = forms.CartForm
                                        )
        if request.method == 'POST' and request.user.is_authenticated:
            d =  request.POST.dict()
            d['form-TOTAL_FORMS'] = products.count()            #https://docs.djangoproject.com/en/4.1/topics/forms/formsets/
            d['form-INITIAL_FORMS'] = '0' 
            form = CartFormSet(data = d)
            if form.is_valid():
                for i in form.cleaned_data:
                    qrst = Ordering.objects.filter(user = request.user, product = i['id'].product) 
                    if Ordering.objects.filter(user = request.user, product = i['id'].product) :
                        [ x.delete() for x in qrst ]
                    Ordering.objects.create( 
                        user          = request.user,
                        product       = i['id'].product,
                        qty           = i['qty'],
                        current_price = i['id'].product.price - (i['id'].product.price * i['id'].product.discount / 100) if 
                                                                                    i['id'].product.discount else i['id'].product.price,
                    )
                messages.success(request, 'Ви оформили змовлення, чекайти поки з вами зв\'яжуться')
                return redirect('shop:index')   
        else:
            form = CartFormSet( queryset = products )

        context = {
            'products' : zip(form, products),
        }
    data = request.session.get('cart_pk_list', {})
    if data and not request.user.is_authenticated:
        context = {
            'products' :zip((Product.objects.get(pk = x) for x in data), (data[x] for x in data))
        }
    return render( request, 'shop/cart.html', context)


def clearCart(request : HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        request.user.cartListUser.all().delete()
    if  request.session.get('cart_pk_list', False):
        del request.session['cart_pk_list']
    messages.success(request, 'Ви успішно очистили кошик!')
    return redirect('shop:index')