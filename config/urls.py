from django.contrib import admin
from django.urls import path, include
from news.views import home  # ✅ فقط این یکی

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    #path('accounts/', include('accounts.urls', namespace='accounts')),
    path('donate/', include('donation.urls')),
    path('wallet/', include('wallet.urls')),
    path('', home, name='home'),  # ✅ این حالا درست کار می‌کنه
    path('martyrs/', include('martyrs.urls')),
    path('news/', include('news.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
