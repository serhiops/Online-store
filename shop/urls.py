from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index , name = 'index'),
    path('category/<slug:categorySlug>/', views.ByCategory.as_view(), name = 'by_category'),
    path('category/<slug:categorySlug>/product/<slug:productSlug>/', views.DetailProduct.as_view(), name = 'detail_product'),
    path('cart/', views.CartView.as_view(), name = 'cart')
]
