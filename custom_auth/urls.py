from django.urls import path
from . import views

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('refresh', views.RefreshTokenView.as_view(), name='refresh'),
    path('whoami', views.WhoAmIView.as_view(), name='whoami'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('logout-all', views.LogoutAllView.as_view(), name='logout-all'),
    path('oauth/yandex', views.OAuthYandexView.as_view(), name='oauth-yandex'),
    path('oauth/yandex/callback', views.OAuthYandexCallbackView.as_view(), name='oauth-yandex-callback'),
    path('forgot-password', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password', views.ResetPasswordView.as_view(), name='reset-password'),
]