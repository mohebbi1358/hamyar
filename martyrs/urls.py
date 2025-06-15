from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MartyrViewSet, create_martyr_view, martyr_list, martyr_detail
from . import views

app_name = 'martyrs'

router = DefaultRouter()
router.register(r'martyrs', MartyrViewSet, basename='martyrs')

urlpatterns = [
    path('', include(router.urls)),  # مسیرهای API مربوط به ViewSet
    path('add/', create_martyr_view, name='create_martyr'),
    path('list/', martyr_list, name='martyr_list'),
    path('<int:martyr_id>/', martyr_detail, name='martyr_detail'),  # نمایش و ثبت دل‌نوشته در همین ویو
    path('<int:pk>/edit/', views.MartyrUpdateView.as_view(), name='martyr_edit'),
    
    
]
