# notification/urls.py

from django.urls import path
from . import views
from django.urls import path
from django.urls import path
from news.views import NewsSearchView
from eternals.views import EternalsSearchView
from .views import NotificationGroupDetailView
from .views import PendingNotificationsListView, NotificationApprovalUpdateView

from django.urls import path
from . import views

app_name = 'notification'



urlpatterns = [
    path('create_hidden/', views.create_notification_hidden, name='create_notification_hidden'),

    path('api/notification-group/<int:group_id>/', views.user_coupons_for_group, name='notification_group_api'),

    path('read/', views.read_notifications_list, name='read_notifications_list'),

    path('mark_read/', views.mark_read, name='mark_read'),

    path('coupons/', views.coupon_list, name='coupon-list'),

    path('pending/', PendingNotificationsListView.as_view(), name='pending_notifications_list'),
    path('pending/<int:pk>/edit/', NotificationApprovalUpdateView.as_view(), name='notification_approval_edit'),

    path('api/unread-count/', views.unread_notifications_count, name='unread_notifications_count'),

    #path('api/notification-group/<int:pk>/', NotificationGroupDetailView.as_view(), name='notification_group_detail'),

    path('news-search/', NewsSearchView.as_view(), name='news_search'),
    path('eternals-search/', EternalsSearchView.as_view(), name='eternals_search'),
    path('create/', views.create_notification, name='create_notification'),
    

    #path('ajax/search-eternals/', views.ajax_search_eternals, name='ajax_search_eternals'),
    #path('ajax/search-news/', views.ajax_search_news, name='ajax_search_news'),
    #path('ajax/eternals/', ajax_search_eternals, name='ajax_search_eternals'),
    #path('ajax/news/', ajax_search_news, name='ajax_search_news'),
    path('unread/', views.unread_notifications_list, name='unread_notifications_list'),
    path('detail/<int:pk>/', views.notification_detail, name='notification_detail'),

    path('groups/', views.notification_group_list, name='notification_group_list'),
    path('groups/create/', views.notification_group_create, name='notification_group_create'),
    path('groups/<int:pk>/edit/', views.notification_group_edit, name='notification_group_edit'),
    path('groups/<int:pk>/delete/', views.notification_group_delete, name='notification_group_delete'),

    path('', views.notifications_list, name='notifications_list'),   # لیست پیام‌ها
    path('create/', views.create_notification, name='create_notification'),  # ارسال پیام جدید
    path('buy-coupon/', views.buy_coupon, name='buy_coupon'),   # خرید کوپن
    path('<int:pk>/', views.notification_detail, name='notification_detail'),  # جزئیات پیام
    path('settings/', views.notification_settings, name='notification_settings'),


]




