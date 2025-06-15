from django.db import models
from django.conf import settings

from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='نام')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='نامک')  # کاربر خودش وارد می‌کند

    def __str__(self):
        return self.name

class News(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='news_items')
    title = models.CharField(max_length=200)
    summary = models.TextField()
    body = models.TextField()
    main_image = models.ImageField(upload_to='news/main_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news/extra_images/')
