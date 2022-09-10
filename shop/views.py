from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from .models import Category, Product
from django.views.generic import ListView, DetailView

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

    def get_queryset(self):
        return Product.objects.filter(category__slug = self.kwargs['categorySlug'], is_active = True)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active = True)
        context['currentCategory'] = Category.objects.get(slug = self.kwargs['categorySlug'])
        return context

class DetailProduct(DetailView):
    model = Product
    template_name = 'shop/product/detail_product.html'
    slug_url_kwarg = 'productSlug'
    context_object_name = 'product'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active = True)
        context['currentCategory'] = Category.objects.get(slug = self.kwargs['categorySlug'])
        context['relatedProducts'] = Product.objects.filter(is_active = True).order_by('?')[:4]
        return context



    

    
    