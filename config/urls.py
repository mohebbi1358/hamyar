# config/urls.py
from django.contrib import admin
from django.urls import path, include
from main.views import home
from news.viewsapi import check_daily_limit_apiview
from django.conf import settings
from django.conf.urls.static import static

# --- Accounts Views ---
from accounts.viewsapi import (
    LoginAPIView,
    VerifyCodeAPIView,
    CompleteProfileAPIView,
    UserAllowedCategoriesView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# --- News Views ---
from news.viewsapi import (
    CategoryListAPI, 
    NewsListAPI, 
    NewsCreateAPI,
    NewsUpdateAPIView, 
    NewsDeleteAPIView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Accounts API ---
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/verify-code/', VerifyCodeAPIView.as_view(), name='api_verify_code'),
    path('api/complete-profile/', CompleteProfileAPIView.as_view(), name='api_complete_profile'),
    path('api/allowed-categories/', UserAllowedCategoriesView.as_view(), name='user-allowed-categories'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- News API ---
    path('api/news/<int:pk>/edit/', NewsUpdateAPIView.as_view(), name='news-edit'),
    path('api/news/<int:pk>/delete/', NewsDeleteAPIView.as_view(), name='news-delete'),
    path('api/categories/', CategoryListAPI.as_view(), name='api_category_list'),
    path('api/news/', NewsListAPI.as_view(), name='api_news_list'),
    path('api/news/create/', NewsCreateAPI.as_view(), name='api_news_create'),
    path('api/news/check-daily-limit/', check_daily_limit_apiview, name='check_daily_limit'),


    # --- Web / Admin / Other ---
    path('accounts/', include('accounts.urls')),
    path('donate/', include(('donation.urls', 'donation'), namespace='donations')),
    path('wallet/', include('wallet.urls')),
    path('', home, name='home'),
    path('martyrs/', include('martyrs.urls')),
    path('news/', include('news.urls')),
    path('eternals/', include(('eternals.urls', 'eternals'), namespace='eternals')),
    path('notifications/', include('notification.urls', namespace='notification')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
