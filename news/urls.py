# news/urls.py
from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('check-daily-limit/', views.check_daily_limit, name='check_daily_limit'),
    path('', views.news_list, name='news_list'),
    path('<int:news_id>/', views.news_detail, name='news_detail'),
    path('create/', views.create_news, name='create_news'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),

]