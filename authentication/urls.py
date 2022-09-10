from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordResetDoneView

app_name = 'authentication'

urlpatterns = [
    path('login/', views.Login.as_view(), name = 'login'),
    path('logout/', views.logoutUser, name = 'logout'),
    path('register/', views.Register.as_view(), name = 'register'),
    
    path('confirm_email/', 
        TemplateView.as_view(template_name = 'authentication/confirm_email.html'), 
        name = 'confirm_email'
    ),
    path('verify_email/<uidb64>/<token>/', views.EmailVerify.as_view(), name = 'verify_email'),
    path('password_reset/', views.PasswordReset.as_view(), name = 'password_reset'),
    
    path('password_reset/password_done/', 
        PasswordResetDoneView.as_view(template_name = 'authentication/confirm_email.html'), 
        name = 'password_reset_done' 
    ),
    path('password_reset_confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name = 'password_reset_confirm'),
]
