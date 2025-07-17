# news/urls.py
from django.urls import path
from . import views
from .views import NewsSearchView 


app_name = 'news'

urlpatterns = [
    path('manage/', views.manage_news, name='manage_news'),
    path('edit/<int:pk>/', views.edit_news, name='edit_news'),
    path('delete/<int:pk>/', views.delete_news, name='delete_news'),

    path('search/', NewsSearchView.as_view(), name='news_search'),
    path('check-daily-limit/', views.check_daily_limit, name='check_daily_limit'),
    path('', views.news_list, name='news_list'),
    path('<int:news_id>/', views.news_detail, name='news_detail'),
    path('create/', views.create_news, name='create_news'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),

]