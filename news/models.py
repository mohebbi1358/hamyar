from django.db import models
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import uuid

def compress_image(image_file, size=None, quality=80, square=False):
    img = Image.open(image_file)
    img = img.convert('RGB')

    if square:
        min_side = min(img.size)
        left = (img.width - min_side) // 2
        top = (img.height - min_side) // 2
        img = img.crop((left, top, left + min_side, top + min_side))

    if size:
        img.thumbnail(size, Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)

    filename = f"{uuid.uuid4().hex}.jpg"
    return filename, ContentFile(buffer.getvalue())

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    daily_limit = models.PositiveIntegerField(default=0)

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

    def save(self, *args, **kwargs):
        try:
            old_instance = News.objects.get(pk=self.pk)
        except News.DoesNotExist:
            old_instance = None

        if self.main_image and hasattr(self.main_image.file, 'read'):
            if not old_instance or self.main_image != old_instance.main_image:
                filename, content = compress_image(
                    self.main_image, size=(500, 500), quality=80, square=True
                )
                self.main_image.save(filename, content, save=False)

        super().save(*args, **kwargs)

class NewsImage(models.Model):
    news = models.ForeignKey(News, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news/extra_images/')

    def save(self, *args, **kwargs):
        try:
            old_instance = NewsImage.objects.get(pk=self.pk)
        except NewsImage.DoesNotExist:
            old_instance = None

        if self.image and hasattr(self.image.file, 'read'):
            if not old_instance or self.image != old_instance.image:
                filename, content = compress_image(
                    self.image, size=(1280, 1280), quality=85, square=False
                )
                self.image.save(filename, content, save=False)

        super().save(*args, **kwargs)

class NewsLink(models.Model):
    news = models.ForeignKey(News, related_name='links', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return f"{self.title} - {self.url}"


class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    persona = models.ForeignKey('accounts.Persona', on_delete=models.CASCADE)
    body = models.TextField(verbose_name='متن نظر')
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.persona.name} | {self.body[:30]}"
