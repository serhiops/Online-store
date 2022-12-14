from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import Category, Product, Cart, TempOrdering, Ordering, Ip, Review
from django.views.generic import ListView, DetailView, FormView, View
from . import forms
from django.urls import reverse_lazy
from django.contrib import messages
from django.forms import Form, modelformset_factory, ModelForm
from .mixins import BaseMixin
from .addintionaly.funcs import getPriceByDiscount , getErrorMessageString, get_client_ip
from django.db.models import Q, Count
from django.core.mail import send_mail
from config.config import GOOGLE_EMAIL_HOST_USER
from .addintionaly.decorators import accessIfCartNotEmpty,accessIf
from heapq import nlargest, nsmallest
from datetime import datetime

class Index(FormView, BaseMixin):
    template_name = 'shop/index.html'
    form_class = forms.SearchForm
    success_url = reverse_lazy('shop:search_products')
    paginate_by = 12

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        #del self.request.session['isInMailingList']
        context['products'] = Product.objects.filter(is_active = True).order_by('?')[:8]
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
        context['title'] = 'Пошук товарів'
        return context

class ByCategory(ListView, BaseMixin):
    template_name = 'shop/product/by_category.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(category__slug = self.kwargs['categorySlug'], is_active = True)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        curCategory = Category.objects.get(slug = self.kwargs['categorySlug'])
        context['currentCategory'] = curCategory
        context['serchMenu'] = True
        context['title'] = 'Категорія : %s' % curCategory.name
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
        product = self.get_object()
        context['currentCategory'] = Category.objects.get(slug = self.kwargs['categorySlug'])
        context['relatedProducts'] = Product.objects.filter(is_active = True, category = product.category).order_by('?')[:4]
        context['countOfReviews']  = Review.objects.filter(product = product).count()
        context['title'] = product.name
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

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        ip = get_client_ip(request)
        if Ip.objects.filter(ip = ip).exists():
            self.get_object().views.add(Ip.objects.get(ip = ip))
        else:
            self.get_object().views.add(Ip.objects.create(ip = ip))
        return super().get(request, *args, **kwargs)

@accessIfCartNotEmpty(reverse_url = 'shop:index')
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
                ordering , _ = Ordering.objects.get_or_create( user = request.user, is_done = False )
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
        productQty = tuple( ( Product.objects.get(pk = x[0]) , x[1] ) for x in data.items() )
        context['products'] = productQty
        context['totalPrice'] = sum( getPriceByDiscount(product) * qty for product, qty in productQty )
    
    context['title'] = 'Кошик'
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
        context['title'] = 'Створення замовлення'
        return context

    def get_form_kwargs(self) -> dict:
        context = super().get_form_kwargs()
        ordering = self.get_object()
        if ordering:
            context['initial'] = {
                'city' : ordering.city,
                'first_name' : ordering.first_name,
                'last_name' : ordering.last_name,
                'post_office' : ordering.post_office,
                'payment' : ordering.payment,
                'number_of_phone': ordering.number_of_phone
            }
        else:
            context['initial'] = {'payment' : 'DBT'}
        return context

class Contact(FormView, BaseMixin):
    template_name = 'shop/contact.html'
    form_class = forms.ContactForm
    success_url = reverse_lazy('shop:index')

    def form_valid(self, form) -> HttpResponse:
        send_mail(
            subject = form.cleaned_data['subject'],
            message = "Повідомлення від користувача сайту : \n%s" % form.cleaned_data['message'],
            from_email = None,
            recipient_list = (GOOGLE_EMAIL_HOST_USER,)
        )
        messages.success(self.request, 'Дякую за повідомлення!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контактна лінія'
        return context

    @accessIf(lambda x: x.is_authenticated)
    def get(self, request: HttpRequest, *args: str, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)

class Reviews(ListView, BaseMixin):
    template_name = 'shop/reviews.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        return Review.objects.filter( product__slug = self.kwargs['productSlug'], is_active = True )

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        currentProduct = Product.objects.get( slug = self.kwargs['productSlug'] )
        context['currentProduct'] = currentProduct
        if self.request.user.is_authenticated:
            ordering = self.request.user.get_user.filter(is_done = True).first()
            if ordering is not None:
                context['isBoughtByUser'] = ordering.tempOrderingList.filter(product = currentProduct).exists()
        context['title'] = 'Коментарі : %s' % currentProduct.name
        return context

class StatisticsForAdmin(View):

    @accessIf(lambda x: x.is_authenticated, 'shop:index')
    def get(self, request, *args, **kwargs) -> HttpRequest:
        products_for_day = [ (product.getCountOfTodaysIP(), product) for product in Product.objects.filter(is_active=True).prefetch_related('views') ]
        product_for_all_time = Product.objects.filter(is_active=True).annotate(cnt=Count('views'))
        total_visits = Ip.objects.all()
        total_orderings = Ordering.objects.all()
        context = {
            'most_popular_for_day'   : nlargest(3, products_for_day ,key=lambda x:x[0]),
            'most_unpopular_for_day' : nsmallest(3, products_for_day ,key=lambda x:x[0]),
            'most_popular_for_all'   : product_for_all_time.order_by('-cnt')[:3],
            'most_unpopular_for_all' : product_for_all_time.order_by('cnt')[:3],
            'total_visits'           : total_visits.count(),
            'visits_for_day'         : total_visits.filter(last_time__contains = datetime.today().date()).count(),
            'count_of_todays_orders' : total_orderings.filter(created__contains = datetime.today().date()).count(),
            'total_orders'           : total_orderings.count(),
            'product_in_cart'        : Product.objects.annotate(cnt=Count('cartListProduct')).order_by('-cnt')[:3]
        }
       
        return render(request, 'admin/main_statistics.html', context)