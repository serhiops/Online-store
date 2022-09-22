from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.Index.as_view(), name = 'index'),
    path('category/<slug:categorySlug>/', views.ByCategory.as_view(), name = 'by_category'),
    path('category/<slug:categorySlug>/product/<slug:productSlug>/', views.DetailProduct.as_view(), name = 'detail_product'),
    path('cart/', views.cartView, name = 'cart'),
    path('clear_cart/', views.clearCart, name = 'clear_cart'),
    path('create_ordering/', views.CreateOrdering.as_view(), name = 'create_ordering'),
    path('search_products/', views.SearchProducts.as_view(), name = 'search_products'),
    path('add_to_mailing_list/', views.addToMailingList, name = 'add_to_mailing_list'),
    path('contact/', views.Contact.as_view(), name = 'contact'),
]
