from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, TwoFactorSetupView, ProtectedView, GoogleLoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('google/', GoogleLoginView.as_view(), name='google_login'),
    path('2fa/setup/', TwoFactorSetupView.as_view(), name='two_factor_setup'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedView.as_view(), name='protected'),
]