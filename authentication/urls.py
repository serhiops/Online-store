from django.urls import path
from . import views

urlpatterns = [
    path('accounts/login/', views.LoginView.as_view(), name = 'account_login'),
    path('accounts/password/reset/key/done/', views.redirectAfterPasswordReset),
    path('accounts/signup/', views.SignupView.as_view(), name = 'account_signup')
]
