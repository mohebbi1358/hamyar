from django.contrib import admin
from django.urls import path, include
from main.views import home
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
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

