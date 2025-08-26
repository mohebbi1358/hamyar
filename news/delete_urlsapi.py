# news/api_urls.py
from django.urls import path
from .viewsapi import (
    CategoryListAPI,
    NewsListAPI,
    NewsCreateAPI
)

urlpatterns = [
    path('categories/', CategoryListAPI.as_view(), name='api_category_list'),
    path('news/', NewsListAPI.as_view(), name='api_news_list'),
    path('news/create/', NewsCreateAPI.as_view(), name='api_news_create'),
]
