from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from .models import Category, Product, Cart
from django.views.generic import ListView, DetailView, FormView
from . import forms
from django.urls import reverse_lazy
from django.contrib import messages
from django.forms import Form

def index(request : HttpRequest) -> HttpResponse:
    categories = Category.objects.filter(is_active = True)
    products = Product.objects.filter(is_active = True)[:8]  
    context = {
        'categories' : categories,
        'products' : products,
    }
    return render(request, 'shop/index.html', context)

class ByCategory(ListView):
    template_name = 'shop/product/by_category.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(category__slug = self.kwargs['categorySlug'], is_active = True)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active = True)
        context['currentCategory'] = Category.objects.get(slug = self.kwargs['categorySlug'])
        return context

class DetailProduct(DetailView, FormView):
    model = Product
    form_class = forms.AddToCartForm
    template_name = 'shop/product/detail_product.html'
    slug_url_kwarg = 'productSlug'
    context_object_name = 'product'
    success_url = reverse_lazy('shop:cart')

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active = True)
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
        messages.error(self.request, 'Помилка :(')
        return super().form_invalid(form)

class CartView(FormView, ListView):
    template_name = 'shop/cart.html'
    success_url = reverse_lazy('shop:index')
    context_object_name = 'products'
    form_class = forms.AddToCartForm

    def get_queryset(self) -> list:
        data = self.request.session.get('cart_pk_list', False)
        if data:
            return { Product.objects.get(pk = x) : data[x] for x in data }

        if self.request.user.is_authenticated:
            return { x.product : x.qty for x in Cart.objects.filter(user = self.request.user) }
        return []

    def form_valid(self, form: Form) -> HttpResponse:
        print(form.cleaned_data)
        return super().form_valid(form)