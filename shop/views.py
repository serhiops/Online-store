from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import Category, Product, Cart, TempOrdering, Ordering, MailingList
from django.views.generic import ListView, DetailView, FormView
from . import forms
from django.urls import reverse_lazy
from django.contrib import messages
from django.forms import Form, modelformset_factory, ModelForm
from .mixins import BaseMixin
from .addintionaly.funcs import getPriceByDiscount , getErrorMessageString
from django.db.models import Q
from django.core.mail import send_mail
from config.config import GOOGLE_EMAIL_HOST_USER

class Index(FormView, BaseMixin):
    template_name = 'shop/index.html'
    form_class = forms.SearchForm
    success_url = reverse_lazy('shop:search_products')
    paginate_by = 12

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        #del self.request.session['isInMailingList']
        context['products'] = Product.objects.filter(is_active = True)[:8]
        context['serchMenu'] = True
        return context

class SearchProducts(ListView, BaseMixin):
    template_name = 'shop/product/by_category.html'
    context_object_name = 'products'

    def get_queryset(self):
        text = self.request.GET['text']
        return Product.objects.filter(Q(name__icontains = text) | Q(description__icontains = text))

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        count = self.get_queryset().count()

        context['serchText'] = self.request.GET['text']
        context['serchPage'] = True
        context['messageText'] = 'По запиту %s знайдено %d товарів!' % (self.request.GET['text'], count)
        context['messageType'] = 'success' if count else 'danger'
        return context

class ByCategory(ListView, BaseMixin):
    template_name = 'shop/product/by_category.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(category__slug = self.kwargs['categorySlug'], is_active = True)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['currentCategory'] = Category.objects.get(slug = self.kwargs['categorySlug'])
        context['serchMenu'] = True
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
        if self.request.user.is_authenticated:
            Cart.objects.filter(product = product, user = self.request.user).delete()
            Cart.objects.create(product = product, user = self.request.user, qty = form.cleaned_data.get('qty', 1))
        else:
            cart_pk_list = self.request.session.get('cart_pk_list', {})
            if cart_pk_list.get(product.pk, False):
                del cart_pk_list[product.pk]
            cart_pk_list[product.pk] = form.cleaned_data.get('qty', 0)
            self.request.session['cart_pk_list'] = cart_pk_list
        messages.success(self.request, 'Ви успішно додали товар до кошика!')
        return super().form_valid(form)

    def form_invalid(self, form: Form) -> HttpResponse:
        messages.error(self.request, form.errors.as_text())
        return super().form_invalid(form)

def cartView(request : HttpRequest) -> HttpResponse:
    products = list()
    context = dict()
    context = {
        'categories' : Category.objects.filter(is_active = True),
        'cartSize'   : request.user.cartListUser.all().count() if request.user.is_authenticated else len(request.session.get('cart_pk_list', {}))
    }
    if request.user.is_authenticated:
 
        products = request.user.cartListUser.select_related('product').all()    #https://django.fun/tutorials/select_related-i-prefetch_related-v-django/
        CartFormSet = modelformset_factory( 
                                            model = Cart, fields  = ('qty', ), 
                                            extra = 0,    formset = forms.MyFormSet, 
                                            form  = forms.CartForm,
                                        )
        if request.method == 'POST' and request.user.is_authenticated:
            d =  request.POST.dict()
            d['form-TOTAL_FORMS'] = products.count()            #https://docs.djangoproject.com/en/4.1/topics/forms/formsets/
            d['form-INITIAL_FORMS'] = '0' 
            form = CartFormSet(data = d)
            if form.is_valid(): 
                ordering , _ = Ordering.objects.get_or_create( user = request.user )
                TempOrdering.objects.filter(main_ordering = ordering).delete()
                total_price = 0
                tempOrderingList = list()
                for i in form.cleaned_data:
                    cur_price = getPriceByDiscount(i['id'].product)
                    tempOrderingList.append(TempOrdering(
                        product       = i['id'].product,
                        qty           = i['qty'],
                        current_price = cur_price,
                        main_ordering = ordering,
                    ))
                    total_price += cur_price * i['qty']
                TempOrdering.objects.bulk_create(tempOrderingList)
                ordering.total_price = total_price
                ordering.save(update_fields = ('total_price',))
                return redirect('shop:create_ordering')   
        else:
            form = CartFormSet( queryset = products )
            context['products'] =  zip(form, products)
            context['totalPrice'] = sum( getPriceByDiscount(x.product) * x.qty for x in products ) 
    data = request.session.get('cart_pk_list', {})
    if data and not request.user.is_authenticated:
        productQty = { Product.objects.get(pk = x[0]) : x[1] for x in data.items() }.items()
        context['products'] = productQty
        context['totalPrice'] = sum( getPriceByDiscount(product) * qty for product, qty in productQty )

    
    return render( request, 'shop/cart.html', context)

def clearCart(request : HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        request.user.cartListUser.all().delete()
    if  request.session.get('cart_pk_list', False):
        del request.session['cart_pk_list']
    messages.success(request, 'Ви успішно очистили кошик!')
    return redirect('shop:index')

class CreateOrdering(FormView, DetailView, BaseMixin):
    template_name = 'shop/create_ordering.html'
    form_class = forms.OrderingForm
    success_url = reverse_lazy('shop:index')
    context_object_name = 'ordering'

    def form_invalid(self, form: ModelForm) -> HttpResponse:
        messages.error(self.request, getErrorMessageString(form))
        return super().form_invalid(form)

    def get_object(self, queryset = None):
        return self.request.user.get_user.last()

    def form_valid(self, form: ModelForm) -> HttpResponse:
        ordering = self.get_object()
        ordering.first_name = form.cleaned_data['first_name']
        ordering.last_name = form.cleaned_data['last_name']
        ordering.city = form.cleaned_data['city']
        ordering.post_office = form.cleaned_data['post_office']
        ordering.payment = form.cleaned_data['payment']
        ordering.number_of_phone = form.cleaned_data['number_of_phone']
        ordering.save()
        messages.success(self.request, 'Ви успішно подали заявку на замовлення!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict:
        context =  super().get_context_data(**kwargs)
        context['tempOrderings'] = TempOrdering.objects.filter(main_ordering = self.get_object())
        return context

    def get_form_kwargs(self) -> dict:
        context = super().get_form_kwargs()
        ordering = self.get_object()
        context['initial'] = {
            'city' : ordering.city,
            'first_name' : ordering.first_name,
            'last_name' : ordering.last_name,
            'post_office' : ordering.post_office,
            'payment' : ordering.payment
        }
        return context

def addToMailingList(request : HttpRequest) -> JsonResponse:
    mail, create = MailingList.objects.get_or_create(email = request.POST.get('mail', ''))
    request.session['isInMailingList'] = create
    data = {
        'text' : 'Дякую, що підписалися на нашу розсилку!' if create else 'Ця пошта вже підписана на нашу розсилку!',
        'create' : create,
    } 
    return JsonResponse(data)


class Contact(FormView):
    template_name = 'shop/contact.html'
    form_class = forms.ContactForm
    success_url = reverse_lazy('shop:index')

    def form_valid(self, form) -> HttpResponse:
        send_mail(
            subject = form.cleaned_data['subject'],
            message = "Повідомлення від користувача сайту : %s" % form.cleaned_data['message'],
            from_email = None,
            recipient_list = (GOOGLE_EMAIL_HOST_USER,)
        )
        messages.success(self.request, 'Дякую за повідомлення!')
        return super().form_valid(form)
