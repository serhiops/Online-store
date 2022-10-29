from django.urls import path, re_path
from . import views

urlpatterns = [
   re_path(
        r"^accounts/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        views.PasswordResetFromKeyView.as_view(),
        name="account_reset_password_from_key",
    ),
    path('accounts/login/', views.LoginView.as_view(), name = 'account_login'),
    path('accounts/password/reset/key/done/', views.redirectAfterPasswordReset),
    path('accounts/signup/', views.SignupView.as_view(), name = 'account_signup'),
]
