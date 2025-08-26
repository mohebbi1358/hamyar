from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .viewsapi import (
    LoginAPIView,
    VerifyCodeAPIView,
    CompleteProfileAPIView,
    UserAllowedCategoriesView,
)

urlpatterns = [
    # JWT Token URLs
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Custom API endpoints
    path('allowed-categories/', UserAllowedCategoriesView.as_view(), name='user-allowed-categories'),

    path('login/', LoginAPIView.as_view(), name='api_login'),
    path('verify-code/', VerifyCodeAPIView.as_view(), name='api_verify_code'),
    path('complete-profile/', CompleteProfileAPIView.as_view(), name='api_complete_profile'),
]
