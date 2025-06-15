# news/admin.py
from django.contrib import admin
from .models import News, NewsImage, Category

admin.site.register(Category)
admin.site.register(News)
admin.site.register(NewsImage)
