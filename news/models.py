from django.db import models
from django.conf import settings

from django.db import models




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='نام')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='نامک')
    daily_limit = models.PositiveIntegerField(
        verbose_name="سقف ارسال روزانه",
        default=0,
        help_text="اگر صفر باشد محدودیتی ندارد."
    )

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



class NewsLink(models.Model):
    news = models.ForeignKey(News, related_name='links', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="عنوان لینک")  # مثلاً: «لینک ایتا»
    url = models.URLField(verbose_name="آدرس لینک")  # مثلاً: https://eitaa.com/mychannel/post/123

    def __str__(self):
        return f"{self.title} - {self.url}"





class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    persona = models.ForeignKey('accounts.Persona', on_delete=models.CASCADE)
    body = models.TextField(verbose_name='متن نظر')
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)  # برای آینده، الان همه تأیید شده هستن

    def __str__(self):
        return f"{self.persona.name} | {self.body[:30]}"
